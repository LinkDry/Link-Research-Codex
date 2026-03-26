from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from tools.dashboard_renderer import render_dashboard_html, render_portfolio_html
from tools.project_state import (
    build_dashboard_projection,
    build_current_project_status,
    evaluate_project_brief_readiness,
    load_memory_state,
    load_json_file,
    parse_experiment_memory,
    parse_project_brief,
    parse_state_markdown,
    suggest_operator_prompt,
)


SLUG_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
PLACEHOLDER_TIMESTAMP = "2026-03-24T00:00:00+08:00"

LIVE_PROJECT_DIRS = [
    "archive/artifacts",
    "papers/assets",
    "papers/drafts",
    "papers/reviews",
    "plans",
    "workspace/bootstrap",
    "workspace/code",
    "workspace/data",
    "workspace/results",
    "workspace/reviews",
]


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def validate_project_slug(slug: str) -> str:
    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError(f"Invalid project slug: {slug}")
    return slug


def _scaffold_dir(repo_root: Path) -> Path:
    return repo_root / "scaffold" / "project"


def _project_dir(repo_root: Path, slug: str) -> Path:
    return repo_root / "projects" / slug


def _runtime_path(repo_root: Path) -> Path:
    return repo_root / ".link-research" / "runtime.json"


def _portfolio_dashboard_path(repo_root: Path) -> Path:
    return repo_root / ".link-research" / "dashboard" / "index.html"


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _instantiate_state(repo_root: Path, slug: str, title: str, timestamp: str) -> None:
    project_id = f"proj-{slug}"
    template_path = _scaffold_dir(repo_root) / "STATE.md"
    content = template_path.read_text(encoding="utf-8")
    content = content.replace("proj-template", project_id)
    content = content.replace("Template Project", title)
    content = content.replace(PLACEHOLDER_TIMESTAMP, timestamp)
    content = content.replace("projects/<slug>/", f"projects/{slug}/")
    _write_text(_project_dir(repo_root, slug) / "STATE.md", content)


def _instantiate_review_state(repo_root: Path, slug: str, timestamp: str) -> None:
    project_id = f"proj-{slug}"
    template_path = _scaffold_dir(repo_root) / "review-state.json"
    data = load_json_file(template_path)
    data["run_id"] = f"run-bootstrap-{slug}"
    data["project_id"] = project_id
    data["started_at"] = timestamp
    data["updated_at"] = timestamp
    data["finished_at"] = timestamp
    data["summary"] = "Project scaffold created. Replace with active run data when execution begins."
    if data.get("steps"):
        data["steps"][0]["started_at"] = timestamp
        data["steps"][0]["finished_at"] = timestamp
        data["steps"][0]["notes"] = "Bootstrap scaffold created for the live project."
    _write_text(
        _project_dir(repo_root, slug) / "review-state.json",
        json.dumps(data, indent=2),
    )


def _instantiate_project_brief(repo_root: Path, slug: str, title: str, owner: str | None) -> None:
    template_path = _scaffold_dir(repo_root) / "project-brief.md"
    lines = template_path.read_text(encoding="utf-8").splitlines()
    updated_lines: list[str] = []
    for line in lines:
        if line.startswith("- project_title:"):
            updated_lines.append(f"- project_title: {title}")
        elif line.startswith("- project_slug:"):
            updated_lines.append(f"- project_slug: {slug}")
        elif line.startswith("- owner:"):
            updated_lines.append(f"- owner: {owner or ''}")
        else:
            updated_lines.append(line)
    _write_text(_project_dir(repo_root, slug) / "project-brief.md", "\n".join(updated_lines) + "\n")


def _instantiate_experiment_memory(repo_root: Path, slug: str, timestamp: str) -> None:
    template_path = _scaffold_dir(repo_root) / "experiment-memory.md"
    content = template_path.read_text(encoding="utf-8").replace(PLACEHOLDER_TIMESTAMP, timestamp)
    _write_text(_project_dir(repo_root, slug) / "experiment-memory.md", content)


def _copy_static_file(repo_root: Path, slug: str, relative_path: str) -> None:
    source = _scaffold_dir(repo_root) / relative_path
    target = _project_dir(repo_root, slug) / relative_path
    _write_text(target, source.read_text(encoding="utf-8"))


def _load_project_snapshot(repo_root: Path, slug: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    project_root = _project_dir(repo_root, slug)
    state = parse_state_markdown(project_root / "STATE.md")
    experiment = parse_experiment_memory(project_root / "experiment-memory.md")
    review_state = load_json_file(project_root / "review-state.json")
    return state, experiment, review_state


def refresh_project_dashboard(repo_root: Path, slug: str) -> dict[str, Any]:
    project_root = _project_dir(repo_root, slug)
    if not project_root.exists():
        raise ValueError(f"Unknown project slug: {slug}")

    state, experiment, review_state = _load_project_snapshot(repo_root, slug)
    memory_state = load_memory_state(repo_root)
    dashboard = build_dashboard_projection(state, experiment, review_state, memory_state)
    _write_text(project_root / "workspace" / "dashboard-data.json", json.dumps(dashboard, indent=2))
    _write_text(project_root / "workspace" / "dashboard.html", render_dashboard_html(slug, dashboard))
    return {
        "slug": slug,
        "project_path": f"projects/{slug}",
        "data_path": f"projects/{slug}/workspace/dashboard-data.json",
        "html_path": f"projects/{slug}/workspace/dashboard.html",
    }


def refresh_all_dashboards(repo_root: Path) -> list[dict[str, Any]]:
    projects_root = repo_root / "projects"
    if not projects_root.exists():
        return []
    refreshed: list[dict[str, Any]] = []
    for child in sorted(projects_root.iterdir()):
        if not child.is_dir():
            continue
        if not (child / "STATE.md").exists():
            continue
        refreshed.append(refresh_project_dashboard(repo_root, child.name))
    current = load_runtime_pointer(repo_root)
    current_slug = current["current_project_slug"] if current else None
    portfolio_projects: list[dict[str, Any]] = []
    for item in refreshed:
        state = parse_state_markdown(repo_root / item["project_path"] / "STATE.md")
        portfolio_projects.append(
            {
                "slug": item["slug"],
                "project_title": state.get("project_title"),
                "phase": state.get("phase"),
                "project_status": state.get("project_status"),
                "risk_level": state.get("risk_level"),
                "next_action": state.get("next_action"),
                "is_current": item["slug"] == current_slug,
                "dashboard_path": item["html_path"],
            }
        )
    _write_text(_portfolio_dashboard_path(repo_root), render_portfolio_html(portfolio_projects))
    return refreshed


def create_project(repo_root: Path, slug: str, title: str, owner: str | None = None) -> Path:
    validate_project_slug(slug)
    project_dir = _project_dir(repo_root, slug)
    if project_dir.exists():
        raise ValueError(f"Project already exists: {slug}")

    project_dir.mkdir(parents=True)
    for relative_dir in LIVE_PROJECT_DIRS:
        (project_dir / relative_dir).mkdir(parents=True, exist_ok=True)

    timestamp = _timestamp()
    _instantiate_state(repo_root, slug, title, timestamp)
    _instantiate_review_state(repo_root, slug, timestamp)
    _instantiate_project_brief(repo_root, slug, title, owner)
    _instantiate_experiment_memory(repo_root, slug, timestamp)
    _copy_static_file(repo_root, slug, "results.tsv")
    _copy_static_file(repo_root, slug, "decision-tree.md")
    refresh_project_dashboard(repo_root, slug)
    return project_dir


def write_runtime_pointer(repo_root: Path, slug: str) -> dict[str, Any]:
    project_dir = _project_dir(repo_root, slug)
    if not project_dir.exists():
        raise ValueError(f"Unknown project slug: {slug}")

    runtime_state = {
        "current_project_slug": slug,
        "current_project_path": f"projects/{slug}",
        "updated_at": _timestamp(),
    }
    runtime_path = _runtime_path(repo_root)
    runtime_path.parent.mkdir(parents=True, exist_ok=True)
    _write_text(runtime_path, json.dumps(runtime_state, indent=2))
    return runtime_state


def load_runtime_pointer(repo_root: Path) -> dict[str, Any] | None:
    runtime_path = _runtime_path(repo_root)
    if not runtime_path.exists():
        return None
    return load_json_file(runtime_path)


def load_current_project_summary(repo_root: Path) -> dict[str, Any] | None:
    runtime_state = load_runtime_pointer(repo_root)
    if runtime_state is None:
        return None

    slug = runtime_state["current_project_slug"]
    project_dir = _project_dir(repo_root, slug)
    if not project_dir.exists():
        raise ValueError(f"Runtime pointer references missing project: {slug}")

    state, experiment, review_state = _load_project_snapshot(repo_root, slug)
    project_brief = parse_project_brief(project_dir / "project-brief.md")
    brief_status = evaluate_project_brief_readiness(project_brief)

    summary = build_current_project_status(slug, state, experiment, review_state, brief_status)
    summary["project_path"] = f"projects/{slug}"
    summary["dashboard_path"] = f"projects/{slug}/workspace/dashboard.html"
    summary["suggested_prompt"] = suggest_operator_prompt(summary)
    return summary


def list_projects(repo_root: Path) -> list[dict[str, Any]]:
    projects_root = repo_root / "projects"
    if not projects_root.exists():
        return []
    current = load_runtime_pointer(repo_root)
    current_slug = current["current_project_slug"] if current else None

    summaries: list[dict[str, Any]] = []
    for child in sorted(projects_root.iterdir()):
        if not child.is_dir():
            continue
        state_path = child / "STATE.md"
        if not state_path.exists():
            continue
        state = parse_state_markdown(state_path)
        summaries.append(
            {
                "slug": child.name,
                "project_id": state.get("project_id"),
                "project_title": state.get("project_title"),
                "phase": state.get("phase"),
                "project_status": state.get("project_status"),
                "next_action": state.get("next_action"),
                "is_current": child.name == current_slug,
            }
        )
    return summaries
