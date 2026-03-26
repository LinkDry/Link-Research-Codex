import json
import shutil
from pathlib import Path

import pytest

from tools.project_ops import (
    create_project,
    load_runtime_pointer,
    load_current_project_summary,
    refresh_all_dashboards,
    refresh_project_dashboard,
    validate_project_slug,
    write_runtime_pointer,
)
from tools.project_state import (
    build_dashboard_projection,
    load_memory_state,
    load_json_file,
    parse_experiment_memory,
    parse_state_markdown,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def repo_fixture(tmp_path: Path) -> Path:
    shutil.copytree(REPO_ROOT / "scaffold", tmp_path / "scaffold")
    shutil.copytree(REPO_ROOT / "memory", tmp_path / "memory")
    (tmp_path / "projects").mkdir(parents=True, exist_ok=True)
    return tmp_path


def test_validate_project_slug_accepts_safe_slug():
    assert validate_project_slug("demo-project") == "demo-project"


@pytest.mark.parametrize("slug", ["Demo", "bad_slug", "bad slug", "-leading"])
def test_validate_project_slug_rejects_invalid_slug(slug: str):
    with pytest.raises(ValueError):
        validate_project_slug(slug)


def test_create_project_instantiates_live_project_without_template_noise(repo_fixture: Path):
    project_dir = create_project(
        repo_root=repo_fixture,
        slug="demo-project",
        title="Demo Project",
        owner="tester",
    )

    assert project_dir == repo_fixture / "projects" / "demo-project"
    assert (project_dir / "STATE.md").exists()
    assert (project_dir / "experiment-memory.md").exists()
    assert (project_dir / "review-state.json").exists()
    assert (project_dir / "workspace" / "dashboard-data.json").exists()
    assert (project_dir / "workspace" / "dashboard.html").exists()
    assert (project_dir / "workspace" / "bootstrap").exists()
    assert (project_dir / "workspace" / "reviews").exists()
    assert (project_dir / "papers" / "drafts").exists()
    assert not (project_dir / "plans" / "_template-anchor.md").exists()
    assert not (project_dir / "plans" / "_template-experiment-plan.md").exists()
    assert not (project_dir / "workspace" / "reviews" / "exp-template").exists()
    assert not (project_dir / "workspace" / "results" / "rg-template").exists()

    state = parse_state_markdown(project_dir / "STATE.md")
    experiment = parse_experiment_memory(project_dir / "experiment-memory.md")
    review_state = load_json_file(project_dir / "review-state.json")
    dashboard = load_json_file(project_dir / "workspace" / "dashboard-data.json")
    memory_state = load_memory_state(repo_fixture)
    brief = (project_dir / "project-brief.md").read_text(encoding="utf-8")

    assert state["project_id"] == "proj-demo-project"
    assert state["project_title"] == "Demo Project"
    assert state["experiment_memory_path"] == "projects/demo-project/experiment-memory.md"
    assert review_state["project_id"] == "proj-demo-project"
    assert "project_title: Demo Project" in brief
    assert "project_slug: demo-project" in brief
    assert "owner: tester" in brief
    assert dashboard == build_dashboard_projection(state, experiment, review_state, memory_state)


def test_runtime_pointer_round_trip(repo_fixture: Path):
    create_project(repo_root=repo_fixture, slug="demo-project", title="Demo Project")

    runtime_state = write_runtime_pointer(repo_root=repo_fixture, slug="demo-project")

    assert runtime_state["current_project_slug"] == "demo-project"
    assert runtime_state["current_project_path"] == "projects/demo-project"
    assert load_runtime_pointer(repo_root=repo_fixture) == runtime_state


def test_load_current_project_summary_reads_selected_project(repo_fixture: Path):
    create_project(repo_root=repo_fixture, slug="demo-project", title="Demo Project")
    write_runtime_pointer(repo_root=repo_fixture, slug="demo-project")

    summary = load_current_project_summary(repo_root=repo_fixture)

    assert summary is not None
    assert summary["slug"] == "demo-project"
    assert summary["project_title"] == "Demo Project"
    assert summary["phase"] == "phase0"
    assert summary["project_status"] == "idle"
    assert summary["brief_ready"] is False
    assert "research_domain" in summary["brief_missing_fields"]
    assert "project-brief.md" in summary["suggested_prompt"]
    assert "Ask Codex" in summary["suggested_prompt"]
    assert "before starting Phase 1 bootstrap" in summary["suggested_prompt"]


def test_load_current_project_summary_preserves_human_gated_handoff(repo_fixture: Path):
    project_dir = create_project(repo_root=repo_fixture, slug="demo-project", title="Demo Project")
    write_runtime_pointer(repo_root=repo_fixture, slug="demo-project")

    state_path = project_dir / "STATE.md"
    state_text = state_path.read_text(encoding="utf-8")
    state_text = state_text.replace("- phase: phase0", "- phase: phase1")
    state_text = state_text.replace("- project_status: idle", "- project_status: waiting-human")
    state_text = state_text.replace("- active_idea_id: null", "- active_idea_id: idea-demo")
    state_text = state_text.replace("- active_branch_id: null", "- active_branch_id: branch-a")
    state_text = state_text.replace("- current_run_id: null", "- current_run_id: run-bootstrap-demo-project")
    state_text = state_text.replace("- decision_mode: auto-report", "- decision_mode: human-gated")
    state_text = state_text.replace("- human_attention: none", "- human_attention: required-now")
    state_text = state_text.replace(
        "- decision_type: null",
        "- decision_type: phase2-handoff\n- decision_options_ref: projects/demo-project/workspace/reviews/exp-demo/judge-report-02.json#decision-options",
    )
    state_path.write_text(state_text, encoding="utf-8")

    experiment_path = project_dir / "experiment-memory.md"
    experiment_text = experiment_path.read_text(encoding="utf-8")
    experiment_text = experiment_text.replace("| idea_id | null |", "| idea_id | idea-demo |")
    experiment_text = experiment_text.replace("| branch_id | null |", "| branch_id | branch-a |")
    experiment_text = experiment_text.replace("| next_experiment_action | wait-human |", "| next_experiment_action | phase2-ready |")
    experiment_path.write_text(experiment_text, encoding="utf-8")

    review_path = project_dir / "review-state.json"
    review_state = load_json_file(review_path)
    review_state["status"] = "waiting-human"
    review_state["resume_safe"] = False
    review_state["decision_mode"] = "human-gated"
    review_state["decision_type"] = "phase2-handoff"
    review_state["decision_options_ref"] = (
        "projects/demo-project/workspace/reviews/exp-demo/judge-report-02.json#decision-options"
    )
    review_path.write_text(json.dumps(review_state, indent=2), encoding="utf-8")

    summary = load_current_project_summary(repo_root=repo_fixture)

    assert summary is not None
    assert summary["decision_mode"] == "human-gated"
    assert summary["decision_type"] == "phase2-handoff"
    assert summary["run_pointer_status"] == "matched"
    assert "before starting Phase 2" in summary["suggested_prompt"]


def test_refresh_project_dashboard_regenerates_payload_and_html(repo_fixture: Path):
    project_dir = create_project(repo_root=repo_fixture, slug="demo-project", title="Demo Project")
    dashboard_data_path = project_dir / "workspace" / "dashboard-data.json"
    dashboard_html_path = project_dir / "workspace" / "dashboard.html"
    dashboard_data_path.write_text("{}", encoding="utf-8")
    dashboard_html_path.write_text("stale", encoding="utf-8")

    refreshed = refresh_project_dashboard(repo_root=repo_fixture, slug="demo-project")

    data = load_json_file(dashboard_data_path)
    html = dashboard_html_path.read_text(encoding="utf-8")

    assert refreshed["slug"] == "demo-project"
    assert data["project"]["project_title"] == "Demo Project"
    assert "dashboard.html" in refreshed["html_path"]
    assert "Demo Project" in html
    assert "Derived from canonical project files" in html


def test_refresh_all_dashboards_writes_portfolio_index(repo_fixture: Path):
    create_project(repo_root=repo_fixture, slug="demo-project", title="Demo Project")
    create_project(repo_root=repo_fixture, slug="second-project", title="Second Project")
    write_runtime_pointer(repo_root=repo_fixture, slug="demo-project")

    refreshed = refresh_all_dashboards(repo_root=repo_fixture)

    portfolio_path = repo_fixture / ".link-research" / "dashboard" / "index.html"
    html = portfolio_path.read_text(encoding="utf-8")

    assert len(refreshed) == 2
    assert portfolio_path.exists()
    assert "Research Portfolio" in html
    assert "Demo Project" in html
