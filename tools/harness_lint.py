from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from tools.project_state import (
    build_dashboard_projection,
    load_memory_state,
    load_json_file,
    parse_experiment_memory,
    parse_state_markdown,
)


REQUIRED_REPO_FILES = [
    "scaffold/project/STATE.md",
    "scaffold/project/experiment-memory.md",
    "scaffold/project/review-state.json",
    "scaffold/project/results.tsv",
    "scaffold/project/project-brief.md",
    "scaffold/project/decision-tree.md",
    "scaffold/project/workspace/dashboard-data.json",
    "scaffold/project/workspace/bootstrap/.gitkeep",
    "memory/lessons-learned.md",
    "memory/failure-library.md",
]

BARE_ARTIFACT_NAMES = {
    "analysis-report.json",
    "config-snapshot.json",
    "judge-report.json",
}

DELEGATE_CONTEXT_KEYWORDS = [
    "bootstrap sequence",
    "route from canonical state",
    "core steps include",
    "use:",
    "delegate publication execution",
]

DELEGATE_STOPWORDS = {
    "pass",
    "tweak",
    "rethink",
    "archive",
    "branch",
    "consistent",
    "drift-detected",
    "anchor-violation",
    "red-line",
    "phase0",
    "phase1",
    "phase2",
    "cross-phase",
    "pending",
    "running",
    "paused",
    "failed",
    "cancelled",
    "completed",
    "support",
    "auto",
    "auto-report",
    "human-gated",
}


def _add_finding(findings: list[dict[str, Any]], severity: str, code: str, path: str, message: str) -> None:
    findings.append(
        {
            "severity": severity,
            "code": code,
            "path": path,
            "message": message,
        }
    )


def _extract_section_items(text: str, heading: str) -> list[str]:
    items: list[str] = []
    in_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == heading:
            in_section = True
            continue
        if in_section and stripped.startswith("#"):
            break
        if in_section and stripped.startswith("- "):
            item = stripped[2:].strip()
            if item.startswith("`") and item.endswith("`"):
                item = item[1:-1]
            items.append(item)
    return items


def _lint_required_files(repo_root: Path, findings: list[dict[str, Any]]) -> None:
    for relative_path in REQUIRED_REPO_FILES:
        if not (repo_root / relative_path).exists():
            _add_finding(
                findings,
                "error",
                "missing-required-file",
                relative_path,
                "Required scaffold or repository file is missing.",
            )


def _lint_scaffold_dashboard(repo_root: Path, findings: list[dict[str, Any]]) -> None:
    required_paths = [
        repo_root / "scaffold" / "project" / "STATE.md",
        repo_root / "scaffold" / "project" / "experiment-memory.md",
        repo_root / "scaffold" / "project" / "review-state.json",
        repo_root / "scaffold" / "project" / "workspace" / "dashboard-data.json",
    ]
    if not all(path.exists() for path in required_paths):
        return

    state = parse_state_markdown(required_paths[0])
    experiment = parse_experiment_memory(required_paths[1])
    review_state = load_json_file(required_paths[2])
    memory_state = load_memory_state(repo_root)
    expected = build_dashboard_projection(state, experiment, review_state, memory_state)
    actual = load_json_file(required_paths[3])
    if actual != expected:
        _add_finding(
            findings,
            "error",
            "dashboard-projection-mismatch",
            "scaffold/project/workspace/dashboard-data.json",
            "Derived scaffold dashboard is out of sync with canonical scaffold state.",
        )


def _lint_live_dashboards(repo_root: Path, findings: list[dict[str, Any]]) -> None:
    projects_root = repo_root / "projects"
    if not projects_root.exists():
        return

    memory_state = load_memory_state(repo_root)
    for child in sorted(projects_root.iterdir()):
        if not child.is_dir():
            continue
        state_path = child / "STATE.md"
        experiment_path = child / "experiment-memory.md"
        review_path = child / "review-state.json"
        dashboard_path = child / "workspace" / "dashboard-data.json"
        required = [state_path, experiment_path, review_path, dashboard_path]
        if not all(path.exists() for path in required):
            continue

        state = parse_state_markdown(state_path)
        experiment = parse_experiment_memory(experiment_path)
        review_state = load_json_file(review_path)
        expected = build_dashboard_projection(state, experiment, review_state, memory_state)
        actual = load_json_file(dashboard_path)
        if actual != expected:
            _add_finding(
                findings,
                "warning",
                "stale-live-dashboard",
                str(dashboard_path.relative_to(repo_root)).replace("\\", "/"),
                "Live project dashboard projection is stale relative to canonical state. Run refresh-dashboard.",
            )


def _lint_skill_contracts(repo_root: Path, findings: list[dict[str, Any]]) -> None:
    skills_root = repo_root / "skills"
    if not skills_root.exists():
        return

    for skill_path in sorted(skills_root.glob("*/SKILL.md")):
        text = skill_path.read_text(encoding="utf-8")
        writes = set(_extract_section_items(text, "### Write"))
        must_not_write = set(_extract_section_items(text, "### Must Not Write"))
        overlap = sorted(writes & must_not_write)
        for entry in overlap:
            _add_finding(
                findings,
                "error",
                "contract-overlap",
                str(skill_path.relative_to(repo_root)).replace("\\", "/"),
                f"Path appears in both Write and Must Not Write: {entry}",
            )

        for heading in ["### Read", "### Write", "### Must Not Write"]:
            for entry in _extract_section_items(text, heading):
                for artifact_name in BARE_ARTIFACT_NAMES:
                    if artifact_name in entry and "projects/<slug>/" not in entry:
                        _add_finding(
                            findings,
                            "warning",
                            "bare-artifact-ref",
                            str(skill_path.relative_to(repo_root)).replace("\\", "/"),
                            f"Artifact ref should use an explicit project-scoped path instead of bare basename: {entry}",
                        )
                        break

        if "decision_options_ref" in text and "judge-report.json#decision-options" in text:
            _add_finding(
                findings,
                "warning",
                "noncanonical-decision-ref",
                str(skill_path.relative_to(repo_root)).replace("\\", "/"),
                "decision_options_ref should use the full project-scoped judge report path instead of a bare basename fragment.",
            )


def _extract_delegate_tokens(text: str) -> set[str]:
    delegates: set[str] = set()
    in_context = False
    saw_list_item = False
    for line in text.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()

        direct_match = re.search(r"\binvoke\s+`([a-z][a-z0-9-]+)`", stripped, flags=re.IGNORECASE)
        if direct_match:
            token = direct_match.group(1)
            if token not in DELEGATE_STOPWORDS:
                delegates.add(token)

        if any(keyword in lowered for keyword in DELEGATE_CONTEXT_KEYWORDS):
            in_context = True
            saw_list_item = False
            continue

        if not in_context:
            continue

        if not stripped:
            if saw_list_item:
                in_context = False
            continue

        if stripped.startswith("#"):
            in_context = False
            continue

        list_match = re.match(r"^(?:[-*]|\d+\.)\s+`([a-z][a-z0-9-]+)`", stripped)
        if list_match:
            token = list_match.group(1)
            if token not in DELEGATE_STOPWORDS:
                delegates.add(token)
            saw_list_item = True
            continue

        if saw_list_item:
            in_context = False
    return delegates


def _lint_delegate_targets(repo_root: Path, findings: list[dict[str, Any]]) -> None:
    skills_root = repo_root / "skills"
    if not skills_root.exists():
        return

    available_skills = {path.parent.name for path in skills_root.glob("*/SKILL.md")}
    for skill_path in sorted(skills_root.glob("*/SKILL.md")):
        text = skill_path.read_text(encoding="utf-8")
        for delegate in sorted(_extract_delegate_tokens(text)):
            if delegate in available_skills:
                continue
            _add_finding(
                findings,
                "warning",
                "missing-delegate-skill",
                str(skill_path.relative_to(repo_root)).replace("\\", "/"),
                f"Delegated skill target is not present in this repo: {delegate}",
            )


def _lint_runtime_pointer(repo_root: Path, findings: list[dict[str, Any]]) -> None:
    runtime_path = repo_root / ".link-research" / "runtime.json"
    if not runtime_path.exists():
        return

    runtime_state = load_json_file(runtime_path)
    slug = runtime_state.get("current_project_slug")
    expected_path = runtime_state.get("current_project_path")
    actual_project_path = repo_root / "projects" / str(slug)

    if not slug or expected_path != f"projects/{slug}" or not actual_project_path.exists():
        _add_finding(
            findings,
            "error",
            "invalid-runtime-pointer",
            ".link-research/runtime.json",
            "Current project pointer does not resolve to a valid live project.",
        )


def run_harness_lint(repo_root: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    _lint_required_files(repo_root, findings)
    _lint_scaffold_dashboard(repo_root, findings)
    _lint_live_dashboards(repo_root, findings)
    _lint_skill_contracts(repo_root, findings)
    _lint_delegate_targets(repo_root, findings)
    _lint_runtime_pointer(repo_root, findings)

    findings.sort(key=lambda finding: (finding["severity"], finding["code"], finding["path"]))
    error_count = sum(1 for finding in findings if finding["severity"] == "error")
    warning_count = sum(1 for finding in findings if finding["severity"] == "warning")
    return {
        "ok": error_count == 0,
        "error_count": error_count,
        "warning_count": warning_count,
        "findings": findings,
    }
