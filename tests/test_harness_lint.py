import json
import shutil
from pathlib import Path

import pytest

from tools.harness_lint import run_harness_lint
from tools.project_ops import create_project


REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def repo_fixture(tmp_path: Path) -> Path:
    shutil.copytree(REPO_ROOT / "scaffold", tmp_path / "scaffold")
    for name in ["memory", "skills"]:
        shutil.copytree(REPO_ROOT / name, tmp_path / name)
    (tmp_path / "projects").mkdir(parents=True, exist_ok=True)
    return tmp_path


def _finding_codes(report: dict) -> set[str]:
    return {finding["code"] for finding in report["findings"]}


def test_lint_reports_missing_required_scaffold_file(repo_fixture: Path):
    (repo_fixture / "scaffold" / "project" / "STATE.md").unlink()

    report = run_harness_lint(repo_fixture)

    assert "missing-required-file" in _finding_codes(report)
    assert report["error_count"] >= 1


def test_lint_reports_dashboard_projection_mismatch(repo_fixture: Path):
    dashboard_path = repo_fixture / "scaffold" / "project" / "workspace" / "dashboard-data.json"
    dashboard = json.loads(dashboard_path.read_text(encoding="utf-8"))
    dashboard["project"]["project_id"] = "wrong-project"
    dashboard_path.write_text(json.dumps(dashboard, indent=2), encoding="utf-8")

    report = run_harness_lint(repo_fixture)

    assert "dashboard-projection-mismatch" in _finding_codes(report)


def test_lint_warns_when_live_project_dashboard_is_stale(repo_fixture: Path):
    project_dir = create_project(repo_root=repo_fixture, slug="demo-project", title="Demo Project")
    dashboard_path = project_dir / "workspace" / "dashboard-data.json"
    dashboard = json.loads(dashboard_path.read_text(encoding="utf-8"))
    dashboard["project"]["project_status"] = "wrong-status"
    dashboard_path.write_text(json.dumps(dashboard, indent=2), encoding="utf-8")

    report = run_harness_lint(repo_fixture)

    assert "stale-live-dashboard" in _finding_codes(report)


def test_lint_reports_write_and_must_not_write_overlap(repo_fixture: Path):
    skill_dir = repo_fixture / "skills" / "bad-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: bad-skill
description: bad test skill
---

# Bad Skill

## Read / Write Contract

### Write

- `projects/<slug>/STATE.md`

### Must Not Write

- `projects/<slug>/STATE.md`
""",
        encoding="utf-8",
    )

    report = run_harness_lint(repo_fixture)

    assert "contract-overlap" in _finding_codes(report)


def test_lint_reports_missing_delegate_skill(repo_fixture: Path):
    skill_dir = repo_fixture / "skills" / "delegate-bad-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: delegate-bad-skill
description: bad delegate test skill
---

# Delegate Bad Skill

## Protocol

Use:

- `phantom-skill`
""",
        encoding="utf-8",
    )

    report = run_harness_lint(repo_fixture)

    assert "missing-delegate-skill" in _finding_codes(report)


def test_lint_does_not_treat_status_or_mode_tokens_as_missing_skills(repo_fixture: Path):
    report = run_harness_lint(repo_fixture)
    messages = [finding["message"] for finding in report["findings"] if finding["code"] == "missing-delegate-skill"]

    assert not any("async-review" in message for message in messages)
    assert not any("required-now" in message for message in messages)
    assert not any("waiting-human" in message for message in messages)
    assert not any("direction-search" in message for message in messages)
    assert not any("seed-papers" in message for message in messages)


def test_lint_reports_invalid_runtime_pointer(repo_fixture: Path):
    runtime_dir = repo_fixture / ".link-research"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "runtime.json").write_text(
        json.dumps(
            {
                "current_project_slug": "missing-project",
                "current_project_path": "projects/missing-project",
                "updated_at": "2026-03-25T00:00:00+08:00",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    report = run_harness_lint(repo_fixture)

    assert "invalid-runtime-pointer" in _finding_codes(report)


def test_lint_reports_bare_artifact_refs_in_skill_contract(repo_fixture: Path):
    skill_dir = repo_fixture / "skills" / "artifact-bad-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: artifact-bad-skill
description: bad artifact ref skill
---

# Artifact Bad Skill

## Read / Write Contract

### Read

- `analysis-report.json` through canonical refs
- `config-snapshot.json` through canonical refs
""",
        encoding="utf-8",
    )

    report = run_harness_lint(repo_fixture)

    assert "bare-artifact-ref" in _finding_codes(report)


def test_lint_reports_noncanonical_decision_option_ref(repo_fixture: Path):
    skill_dir = repo_fixture / "skills" / "decision-bad-skill"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: decision-bad-skill
description: bad decision ref skill
---

# Decision Bad Skill

Set `decision_options_ref` to `judge-report.json#decision-options`.
""",
        encoding="utf-8",
    )

    report = run_harness_lint(repo_fixture)

    assert "noncanonical-decision-ref" in _finding_codes(report)
