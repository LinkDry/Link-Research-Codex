import json
from pathlib import Path

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


REPO_ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD_DIR = REPO_ROOT / "scaffold" / "project"


def test_parse_state_markdown_reads_scalar_and_list_fields():
    state = parse_state_markdown(SCAFFOLD_DIR / "STATE.md")

    assert state["project_id"] == "proj-template"
    assert state["project_title"] == "Template Project"
    assert state["phase"] == "phase0"
    assert state["current_run_id"] is None
    assert state["blockers"] == []


def test_parse_experiment_memory_reads_active_line_snapshot():
    experiment = parse_experiment_memory(SCAFFOLD_DIR / "experiment-memory.md")

    assert experiment["experiment_id"] is None
    assert experiment["status"] == "planned"
    assert experiment["iteration_count"] == 0
    assert experiment["archive_recommended"] is False
    assert experiment["human_review_required"] is False


def test_build_dashboard_projection_matches_scaffold_fixture():
    state = parse_state_markdown(SCAFFOLD_DIR / "STATE.md")
    experiment = parse_experiment_memory(SCAFFOLD_DIR / "experiment-memory.md")
    review_state = load_json_file(SCAFFOLD_DIR / "review-state.json")
    memory_state = load_memory_state(REPO_ROOT)

    actual = build_dashboard_projection(state, experiment, review_state, memory_state)
    expected = json.loads((SCAFFOLD_DIR / "workspace" / "dashboard-data.json").read_text(encoding="utf-8"))

    assert actual == expected


def test_build_current_project_status_uses_canonical_state():
    state = parse_state_markdown(SCAFFOLD_DIR / "STATE.md")
    experiment = parse_experiment_memory(SCAFFOLD_DIR / "experiment-memory.md")
    review_state = load_json_file(SCAFFOLD_DIR / "review-state.json")

    status = build_current_project_status("demo-project", state, experiment, review_state)

    assert status["slug"] == "demo-project"
    assert status["project_title"] == "Template Project"
    assert status["phase"] == "phase0"
    assert status["project_status"] == "idle"
    assert status["current_run_id"] is None
    assert status["run_status"] is None


def test_suggest_operator_prompt_for_bootstrap_state():
    state = parse_state_markdown(SCAFFOLD_DIR / "STATE.md")
    experiment = parse_experiment_memory(SCAFFOLD_DIR / "experiment-memory.md")
    review_state = load_json_file(SCAFFOLD_DIR / "review-state.json")
    brief = parse_project_brief(SCAFFOLD_DIR / "project-brief.md")
    brief_status = evaluate_project_brief_readiness(brief)
    status = build_current_project_status("demo-project", state, experiment, review_state, brief_status)

    prompt = suggest_operator_prompt(status)

    assert "Ask Codex" in prompt
    assert "project-brief.md" in prompt
    assert "before starting Phase 1 bootstrap" in prompt
    assert "direction_prompt" in prompt


def test_parse_project_brief_and_readiness_detect_incomplete_bootstrap_state():
    brief = parse_project_brief(SCAFFOLD_DIR / "project-brief.md")
    readiness = evaluate_project_brief_readiness(brief)

    assert brief["intake_mode"] == "direction-search"
    assert readiness["brief_ready"] is False
    assert "research_domain" in readiness["missing_fields"]
    assert "direction_prompt" in readiness["missing_fields"]


def test_project_brief_readiness_accepts_seed_papers_mode_with_required_fields():
    brief = {
        "research_domain": "nlp",
        "target_problem": "grounded generation",
        "intended_contribution_type": "method",
        "in_scope": "citation-grounded generation",
        "ethics_and_integrity_red_lines": "no fabricated citations",
        "intake_mode": "seed-papers",
        "seed_papers": "[paper-a, paper-b]",
    }

    readiness = evaluate_project_brief_readiness(brief)

    assert readiness["brief_ready"] is True
    assert readiness["missing_fields"] == []


def test_suggest_operator_prompt_starts_phase1_only_after_brief_is_ready():
    state = parse_state_markdown(SCAFFOLD_DIR / "STATE.md")
    experiment = parse_experiment_memory(SCAFFOLD_DIR / "experiment-memory.md")
    review_state = load_json_file(SCAFFOLD_DIR / "review-state.json")
    ready_brief = {
        "research_domain": "nlp",
        "target_problem": "grounded generation",
        "intended_contribution_type": "method",
        "in_scope": "citation-grounded generation",
        "ethics_and_integrity_red_lines": "no fabricated citations",
        "intake_mode": "direction-search",
        "direction_prompt": "Find a robust grounded generation research line.",
    }
    brief_status = evaluate_project_brief_readiness(ready_brief)
    status = build_current_project_status("demo-project", state, experiment, review_state, brief_status)

    prompt = suggest_operator_prompt(status)

    assert "Ask Codex" in prompt
    assert "Phase 1 bootstrap" in prompt
    assert "before starting Phase 1 bootstrap" not in prompt


def test_suggest_operator_prompt_for_human_gated_phase2_handoff():
    state = parse_state_markdown(SCAFFOLD_DIR / "STATE.md")
    experiment = parse_experiment_memory(SCAFFOLD_DIR / "experiment-memory.md")
    review_state = load_json_file(SCAFFOLD_DIR / "review-state.json")

    state.update(
        {
            "phase": "phase1",
            "project_status": "waiting-human",
            "active_idea_id": "idea-demo",
            "active_branch_id": "branch-a",
            "current_run_id": "run-template",
            "decision_mode": "human-gated",
            "decision_type": "phase2-handoff",
            "decision_options_ref": "projects/demo-project/workspace/reviews/exp-demo/judge-report-02.json#decision-options",
        }
    )
    experiment["idea_id"] = "idea-demo"
    experiment["branch_id"] = "branch-a"
    experiment["next_experiment_action"] = "phase2-ready"
    review_state["run_id"] = "run-template"
    review_state["status"] = "waiting-human"
    review_state["resume_safe"] = False
    review_state["decision_mode"] = "human-gated"
    review_state["decision_type"] = "phase2-handoff"
    review_state["decision_options_ref"] = state["decision_options_ref"]

    status = build_current_project_status("demo-project", state, experiment, review_state)
    prompt = suggest_operator_prompt(status)

    assert status["run_pointer_status"] == "matched"
    assert status["decision_type"] == "phase2-handoff"
    assert "handoff" in prompt.lower()
    assert "before starting Phase 2" in prompt
    assert "judge-report-02.json#decision-options" in prompt


def test_suggest_operator_prompt_flags_stale_run_pointer():
    state = parse_state_markdown(SCAFFOLD_DIR / "STATE.md")
    experiment = parse_experiment_memory(SCAFFOLD_DIR / "experiment-memory.md")
    review_state = load_json_file(SCAFFOLD_DIR / "review-state.json")

    state.update(
        {
            "phase": "phase1",
            "project_status": "running",
            "active_idea_id": "idea-demo",
            "current_run_id": "run-expected",
        }
    )
    review_state["run_id"] = "run-other"
    review_state["status"] = "running"

    status = build_current_project_status("demo-project", state, experiment, review_state)
    prompt = suggest_operator_prompt(status)

    assert status["run_pointer_status"] == "stale"
    assert "does not match" in prompt
    assert "do not continue" in prompt


def test_load_memory_state_reads_structured_sections(tmp_path: Path):
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    (memory_dir / "lessons-learned.md").write_text(
        """# Lessons Learned

## Recent Lessons
| lesson_id | date | scope | project_id | idea_id | branch_id | source_type | category | polarity | summary | source_ref | evidence_ref | reusable | similarity_tags |
|-----------|------|-------|------------|---------|-----------|-------------|----------|----------|---------|------------|--------------|----------|-----------------|
| lesson-001 | 2026-03-25 | project | proj-demo | idea-a | branch-a | archive | evaluation | negative | Metric leaked task difficulty. | projects/demo/archive/archive-exp-001.md | projects/demo/results.tsv#L12 | true | [\"metric\", \"leakage\"] |

## Persistent Patterns
| pattern_id | pattern_type | first_seen | last_seen | occurrence_count | summary | trigger_signals | recommended_action | confidence |
|------------|--------------|------------|-----------|------------------|---------|-----------------|--------------------|------------|
| pattern-001 | evaluation | 2026-03-20 | 2026-03-25 | 2 | Small benchmarks hide regressions. | [\"tiny dataset\"] | Increase dataset breadth. | high |

## Capability Gaps
| gap_id | date | gap_type | impact_level | description | detected_in | workaround | proposed_fix | status |
|--------|------|----------|--------------|-------------|-------------|------------|--------------|--------|
| gap-001 | 2026-03-25 | tooling | medium | No automated ablation summarizer. | literature-review | manual comparison | add summarizer | open |

## Promotion Queue
| source_lesson_refs | proposed_pattern_or_failure_class | reason_for_promotion | status |
|--------------------|----------------------------------|----------------------|--------|
| - | - | - | - |
""",
        encoding="utf-8",
    )
    (memory_dir / "failure-library.md").write_text(
        """# Failure Library

## Failure Cases
| failure_id | project_id | idea_id | branch_id | failure_class | summary | why_it_failed | when_to_warn_again | similarity_tags | hard_red_flags | soft_red_flags | archive_ref | evidence_refs |
|------------|------------|---------|-----------|---------------|---------|---------------|--------------------|-----------------|----------------|----------------|-------------|---------------|
| failure-001 | proj-demo | idea-a | branch-a | benchmark-fragility | Validation collapsed on a broader split. | Benchmark was too narrow. | Warn when eval set is tiny. | [\"evaluation\"] | [\"benchmark leakage\"] | [\"small eval\"] | projects/demo/archive/archive-exp-001.md | [\"projects/demo/results.tsv#L12\"] |
""",
        encoding="utf-8",
    )

    memory_state = load_memory_state(tmp_path)

    assert memory_state["recent_lessons"][0]["lesson_id"] == "lesson-001"
    assert memory_state["active_patterns"][0]["pattern_id"] == "pattern-001"
    assert memory_state["open_capability_gaps"][0]["gap_id"] == "gap-001"
    assert memory_state["recent_warnings"][0]["failure_id"] == "failure-001"


def test_build_dashboard_projection_includes_memory_state():
    state = parse_state_markdown(SCAFFOLD_DIR / "STATE.md")
    experiment = parse_experiment_memory(SCAFFOLD_DIR / "experiment-memory.md")
    review_state = load_json_file(SCAFFOLD_DIR / "review-state.json")
    memory_state = {
        "recent_lessons": [{"lesson_id": "lesson-001", "summary": "Lesson summary"}],
        "active_patterns": [{"pattern_id": "pattern-001", "summary": "Pattern summary"}],
        "open_capability_gaps": [{"gap_id": "gap-001", "description": "Gap summary"}],
        "recent_warnings": [{"failure_id": "failure-001", "summary": "Failure summary"}],
    }

    dashboard = build_dashboard_projection(state, experiment, review_state, memory_state)

    assert dashboard["project"]["project_title"] == "Template Project"
    assert dashboard["project"]["decision_mode"] == "auto-report"
    assert dashboard["memory"]["recent_lessons"][0]["lesson_id"] == "lesson-001"
    assert dashboard["memory"]["recent_warnings"][0]["failure_id"] == "failure-001"
