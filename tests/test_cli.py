from pathlib import Path

import pytest

from tools.link_research_cli import main
from tools.project_ops import create_project, load_runtime_pointer


@pytest.fixture()
def repo_fixture(tmp_path: Path) -> Path:
    source_root = Path(__file__).resolve().parents[1]
    import shutil

    shutil.copytree(source_root / "scaffold", tmp_path / "scaffold")
    shutil.copytree(source_root / "memory", tmp_path / "memory")
    shutil.copytree(source_root / "skills", tmp_path / "skills")
    (tmp_path / "projects").mkdir(parents=True, exist_ok=True)
    return tmp_path


def test_cli_new_project_creates_project_and_reports_success(repo_fixture: Path, capsys: pytest.CaptureFixture[str]):
    exit_code = main(
        ["new-project", "--slug", "demo-project", "--title", "Demo Project", "--owner", "tester"],
        repo_root=repo_fixture,
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Created project demo-project" in captured.out
    assert (repo_fixture / "projects" / "demo-project").exists()


def test_cli_list_projects_marks_current_project(repo_fixture: Path, capsys: pytest.CaptureFixture[str]):
    create_project(repo_fixture, "demo-project", "Demo Project")
    create_project(repo_fixture, "second-project", "Second Project")
    main(["switch-project", "--slug", "second-project"], repo_root=repo_fixture)

    exit_code = main(["list-projects"], repo_root=repo_fixture)

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "demo-project" in captured.out
    assert "* second-project" in captured.out


def test_cli_switch_project_updates_runtime_pointer(repo_fixture: Path, capsys: pytest.CaptureFixture[str]):
    create_project(repo_fixture, "demo-project", "Demo Project")

    exit_code = main(["switch-project", "--slug", "demo-project"], repo_root=repo_fixture)

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Current project set to demo-project" in captured.out
    assert load_runtime_pointer(repo_fixture)["current_project_slug"] == "demo-project"


def test_cli_returns_non_zero_for_missing_project(repo_fixture: Path, capsys: pytest.CaptureFixture[str]):
    exit_code = main(["switch-project", "--slug", "missing-project"], repo_root=repo_fixture)

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Unknown project slug" in captured.err


def test_cli_harness_lint_runs_and_reports_summary(repo_fixture: Path, capsys: pytest.CaptureFixture[str]):
    exit_code = main(["harness-lint"], repo_root=repo_fixture)

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Harness lint:" in captured.out
    assert "warning" in captured.out.lower()


def test_readme_documents_cli_quickstart():
    readme = Path(__file__).resolve().parents[1] / "README.md"

    assert readme.exists()
    content = readme.read_text(encoding="utf-8")
    assert "python -m tools.link_research_cli new-project" in content
    assert "python -m tools.link_research_cli harness-lint" in content
    assert "python -m tools.link_research_cli current-project" in content
    assert "python -m tools.link_research_cli refresh-dashboard" in content
    assert ".link-research/dashboard/index.html" in content
    assert "scaffold/project/" in content
    assert "docs/guides/phase1-quickstart.md" in content
    assert "docs/guides/recovery-and-resume.md" in content
    assert "docs/guides/dashboard-usage.md" in content
    assert "docs/history-summary.md" in content
    assert "codex --version" in content
    assert "python -m tools.link_research_cli codex-healthcheck" in content
    assert 'codex exec -m gpt-5.4 "Reply with exactly: GPT54_OK"' in content
    assert "novelty-check" in content
    assert "phase2-publish" in content
    assert "lowercase letters, numbers, and hyphens only" in content
    assert "Agent.md" in content
    assert "Codex-first" in content
    assert "Claude-first" not in content
    assert "claude mcp add codex" not in content
    assert "Link-Research V2" not in content
    assert "V2 rebuild" not in content


def test_root_agent_entrypoint_exists_and_points_to_live_surface():
    repo_root = Path(__file__).resolve().parents[1]
    agent = repo_root / "Agent.md"
    legacy = repo_root / "CLAUDE.md"

    assert agent.exists()
    assert not legacy.exists()
    content = agent.read_text(encoding="utf-8")
    assert "current-project" in content
    assert "phase1-quickstart.md" in content
    assert "STATE.md" in content
    assert "Codex" in content
    assert "GPT-5.4" in content
    assert "novelty-check" in content
    assert "docs/history-summary.md" in content
    assert "docs/plans/" not in content
    assert "Claude" not in content


def test_operator_guides_exist():
    repo_root = Path(__file__).resolve().parents[1]
    quickstart = repo_root / "docs" / "guides" / "phase1-quickstart.md"
    recovery = repo_root / "docs" / "guides" / "recovery-and-resume.md"
    dashboard = repo_root / "docs" / "guides" / "dashboard-usage.md"

    assert quickstart.exists()
    assert recovery.exists()
    assert dashboard.exists()
    assert "Phase 1" in quickstart.read_text(encoding="utf-8")
    assert "resume" in recovery.read_text(encoding="utf-8").lower()
    assert "portfolio" in dashboard.read_text(encoding="utf-8").lower()


def test_cli_current_project_reports_status_and_prompt(repo_fixture: Path, capsys: pytest.CaptureFixture[str]):
    create_project(repo_fixture, "demo-project", "Demo Project")
    main(["switch-project", "--slug", "demo-project"], repo_root=repo_fixture)

    exit_code = main(["current-project"], repo_root=repo_fixture)

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Current project: demo-project" in captured.out
    assert "Phase: phase0" in captured.out
    assert "Brief ready: no" in captured.out
    assert "Missing brief fields:" in captured.out
    assert "Next action:" in captured.out
    assert "Suggested Codex prompt:" in captured.out


def test_cli_current_project_handles_missing_runtime_pointer(repo_fixture: Path, capsys: pytest.CaptureFixture[str]):
    exit_code = main(["current-project"], repo_root=repo_fixture)

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "No current project selected" in captured.err
    assert "new-project" in captured.err
    assert "switch-project" in captured.err


def test_cli_refresh_dashboard_handles_missing_runtime_pointer(repo_fixture: Path, capsys: pytest.CaptureFixture[str]):
    exit_code = main(["refresh-dashboard"], repo_root=repo_fixture)

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "new-project" in captured.err
    assert "switch-project" in captured.err


def test_cli_current_project_surfaces_human_gated_phase2_handoff(
    repo_fixture: Path,
    capsys: pytest.CaptureFixture[str],
):
    project_dir = create_project(repo_fixture, "demo-project", "Demo Project")
    main(["switch-project", "--slug", "demo-project"], repo_root=repo_fixture)

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
    review_text = review_path.read_text(encoding="utf-8")
    review_text = review_text.replace('"status": "completed"', '"status": "waiting-human"')
    review_text = review_text.replace('"resume_safe": false', '"resume_safe": false')
    review_text = review_text.replace('"decision_mode": "auto-report"', '"decision_mode": "human-gated"')
    review_text = review_text.replace('"decision_type": null', '"decision_type": "phase2-handoff"')
    review_text = review_text.replace(
        '"decision_options_ref": null',
        '"decision_options_ref": "projects/demo-project/workspace/reviews/exp-demo/judge-report-02.json#decision-options"',
    )
    review_path.write_text(review_text, encoding="utf-8")

    exit_code = main(["current-project"], repo_root=repo_fixture)

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Decision mode: human-gated" in captured.out
    assert "Decision type: phase2-handoff" in captured.out
    assert "before starting Phase 2" in captured.out


def test_cli_refresh_dashboard_current_project_writes_html(repo_fixture: Path, capsys: pytest.CaptureFixture[str]):
    project_dir = create_project(repo_fixture, "demo-project", "Demo Project")
    main(["switch-project", "--slug", "demo-project"], repo_root=repo_fixture)

    exit_code = main(["refresh-dashboard"], repo_root=repo_fixture)

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Refreshed dashboard for demo-project" in captured.out
    assert (project_dir / "workspace" / "dashboard.html").exists()


def test_cli_refresh_dashboard_all_projects(repo_fixture: Path, capsys: pytest.CaptureFixture[str]):
    create_project(repo_fixture, "demo-project", "Demo Project")
    create_project(repo_fixture, "second-project", "Second Project")

    exit_code = main(["refresh-dashboard", "--all"], repo_root=repo_fixture)

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "demo-project" in captured.out
    assert "second-project" in captured.out
    assert ".link-research/dashboard/index.html" in captured.out


def test_cli_codex_healthcheck_reports_success(
    repo_fixture: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        "tools.link_research_cli.run_codex_healthcheck",
        lambda: {"ok": True, "message": "Codex reached GPT-5.4 and returned GPT54_OK."},
    )

    exit_code = main(["codex-healthcheck"], repo_root=repo_fixture)

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "GPT54_OK" in captured.out


def test_docs_history_summary_replaces_old_history_dirs():
    repo_root = Path(__file__).resolve().parents[1]

    assert (repo_root / "docs" / "history-summary.md").exists()
    assert not (repo_root / "docs" / "plans").exists()
    assert not (repo_root / "docs" / "skills").exists()
