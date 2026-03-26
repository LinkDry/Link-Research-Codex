from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json_file(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _coerce_value(raw: str) -> Any:
    value = raw.strip()
    if value == "null":
        return None
    if value == "true":
        return True
    if value == "false":
        return False
    if value.startswith('"') and value.endswith('"'):
        return json.loads(value)
    if value.startswith("[") and value.endswith("]"):
        return json.loads(value)
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def parse_state_markdown(path: Path) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("- ") or ":" not in stripped:
            continue
        key, raw_value = stripped[2:].split(":", 1)
        fields[key.strip()] = _coerce_value(raw_value)
    return fields


def parse_project_brief(path: Path) -> dict[str, Any]:
    return parse_state_markdown(path)


def _is_missing_brief_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list):
        return len(value) == 0
    return False


def evaluate_project_brief_readiness(project_brief: dict[str, Any]) -> dict[str, Any]:
    missing_fields: list[str] = []
    required_fields = [
        "research_domain",
        "target_problem",
        "intended_contribution_type",
        "in_scope",
        "ethics_and_integrity_red_lines",
        "intake_mode",
    ]

    for field in required_fields:
        if _is_missing_brief_value(project_brief.get(field)):
            missing_fields.append(field)

    intake_mode = project_brief.get("intake_mode")
    if intake_mode == "direction-search":
        if _is_missing_brief_value(project_brief.get("direction_prompt")):
            missing_fields.append("direction_prompt")
    elif intake_mode == "seed-papers":
        if _is_missing_brief_value(project_brief.get("seed_papers")):
            missing_fields.append("seed_papers")

    return {
        "brief_ready": len(missing_fields) == 0,
        "missing_fields": missing_fields,
    }


def parse_experiment_memory(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").splitlines()
    in_snapshot = False
    rows: dict[str, Any] = {}
    for line in lines:
        stripped = line.strip()
        if stripped == "## Active Line Snapshot":
            in_snapshot = True
            continue
        if in_snapshot and stripped.startswith("## "):
            break
        if not in_snapshot or not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != 2:
            continue
        field, value = cells
        if field in {"Field", "------"}:
            continue
        if value in {"Value", "-------"}:
            continue
        rows[field] = _coerce_value(value)
    return rows


def _parse_markdown_table_section(text: str, heading: str) -> list[dict[str, Any]]:
    lines = text.splitlines()
    in_section = False
    table_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == heading:
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if in_section and stripped.startswith("|"):
            table_lines.append(stripped)

    if len(table_lines) < 3:
        return []

    headers = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    rows: list[dict[str, Any]] = []
    for line in table_lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        row = {header: _coerce_value(value) for header, value in zip(headers, cells)}
        first_header = headers[0]
        if row.get(first_header) == "-":
            continue
        rows.append(row)
    return rows


def load_memory_state(repo_root: Path) -> dict[str, Any]:
    lessons_path = repo_root / "memory" / "lessons-learned.md"
    failure_path = repo_root / "memory" / "failure-library.md"

    lessons_text = lessons_path.read_text(encoding="utf-8") if lessons_path.exists() else ""
    failures_text = failure_path.read_text(encoding="utf-8") if failure_path.exists() else ""

    recent_lessons = _parse_markdown_table_section(lessons_text, "## Recent Lessons")
    active_patterns = _parse_markdown_table_section(lessons_text, "## Persistent Patterns")
    capability_gaps = _parse_markdown_table_section(lessons_text, "## Capability Gaps")
    recent_warnings = _parse_markdown_table_section(failures_text, "## Failure Cases")

    open_capability_gaps = [
        gap
        for gap in capability_gaps
        if str(gap.get("status", "")).lower() not in {"resolved", "closed", "done"}
    ]

    return {
        "recent_lessons": recent_lessons,
        "active_patterns": active_patterns,
        "open_capability_gaps": open_capability_gaps,
        "recent_warnings": recent_warnings,
    }


def build_dashboard_projection(
    state: dict[str, Any],
    experiment: dict[str, Any],
    review_state: dict[str, Any],
    memory_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    run_is_active = state.get("current_run_id") and review_state.get("run_id") == state.get("current_run_id")
    memory_state = memory_state or {
        "recent_lessons": [],
        "active_patterns": [],
        "open_capability_gaps": [],
        "recent_warnings": [],
    }
    run_block: dict[str, Any]
    if run_is_active:
        run_block = {
            "run_id": review_state.get("run_id"),
            "status": review_state.get("status"),
            "current_step_name": review_state.get("current_step_name"),
            "human_attention": review_state.get("human_attention"),
            "resume_safe": review_state.get("resume_safe"),
            "blocking_reason": review_state.get("blocking_reason"),
        }
    else:
        run_block = {
            "run_id": None,
            "status": None,
            "current_step_name": None,
            "human_attention": state.get("human_attention", "none"),
            "resume_safe": False,
            "blocking_reason": None,
        }

    return {
        "meta": {
            "generated_at": state.get("last_updated"),
            "schema_version": "schema-2026-03",
            "is_derived": True,
        },
        "project": {
            "project_id": state.get("project_id"),
            "project_title": state.get("project_title"),
            "phase": state.get("phase"),
            "project_status": state.get("project_status"),
            "next_action": state.get("next_action"),
            "risk_level": state.get("risk_level"),
            "decision_mode": state.get("decision_mode"),
            "decision_type": state.get("decision_type"),
            "human_attention": state.get("human_attention"),
            "active_idea_id": state.get("active_idea_id"),
            "active_branch_id": state.get("active_branch_id"),
            "blockers": state.get("blockers", []),
        },
        "experiment": {
            "experiment_id": experiment.get("experiment_id"),
            "idea_id": experiment.get("idea_id"),
            "branch_id": experiment.get("branch_id"),
            "status": experiment.get("status"),
            "latest_judge_verdict": experiment.get("latest_judge_verdict"),
            "latest_drift_score": experiment.get("latest_drift_score"),
            "next_experiment_action": experiment.get("next_experiment_action"),
        },
        "run": run_block,
        "memory": {
            "recent_lessons": memory_state.get("recent_lessons", []),
            "recent_warnings": memory_state.get("recent_warnings", []),
            "active_patterns": memory_state.get("active_patterns", []),
            "open_capability_gaps": memory_state.get("open_capability_gaps", []),
        },
    }


def build_current_project_status(
    slug: str,
    state: dict[str, Any],
    experiment: dict[str, Any],
    review_state: dict[str, Any],
    brief_status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    brief_status = brief_status or {"brief_ready": True, "missing_fields": []}
    current_run_id = state.get("current_run_id")
    review_run_id = review_state.get("run_id")
    if current_run_id is None:
        run_pointer_status = "none"
    elif review_run_id == current_run_id:
        run_pointer_status = "matched"
    else:
        run_pointer_status = "stale"

    review_matches_state = run_pointer_status == "matched"

    return {
        "slug": slug,
        "project_title": state.get("project_title"),
        "phase": state.get("phase"),
        "project_status": state.get("project_status"),
        "decision_mode": state.get("decision_mode"),
        "decision_type": state.get("decision_type"),
        "decision_options_ref": state.get("decision_options_ref"),
        "active_idea_id": state.get("active_idea_id") or experiment.get("idea_id"),
        "active_branch_id": state.get("active_branch_id") or experiment.get("branch_id"),
        "current_run_id": current_run_id,
        "run_pointer_status": run_pointer_status,
        "run_status": review_state.get("status") if review_matches_state else None,
        "current_step_name": review_state.get("current_step_name") if review_matches_state else None,
        "resume_safe": review_state.get("resume_safe") if review_matches_state else False,
        "review_decision_mode": review_state.get("decision_mode") if review_matches_state else None,
        "review_decision_type": review_state.get("decision_type") if review_matches_state else None,
        "review_decision_options_ref": (
            review_state.get("decision_options_ref") if review_matches_state else None
        ),
        "human_attention": (
            review_state.get("human_attention")
            if review_matches_state
            else state.get("human_attention")
        ),
        "next_action": state.get("next_action"),
        "next_experiment_action": experiment.get("next_experiment_action"),
        "latest_judge_verdict": experiment.get("latest_judge_verdict"),
        "latest_drift_score": experiment.get("latest_drift_score"),
        "brief_ready": brief_status.get("brief_ready", True),
        "brief_missing_fields": brief_status.get("missing_fields", []),
    }


def suggest_operator_prompt(status: dict[str, Any]) -> str:
    project_root = f"projects/{status['slug']}"
    current_run_id = status.get("current_run_id")
    run_status = status.get("run_status")
    run_pointer_status = status.get("run_pointer_status")

    if run_pointer_status == "stale":
        return (
            f"Ask Codex to inspect {project_root}/STATE.md and {project_root}/review-state.json before "
            f"resuming. The current run pointer {current_run_id} does not match the run-state file, "
            f"so do not continue execution until the mismatch is resolved."
        )

    decision_mode = status.get("decision_mode")
    decision_type = status.get("decision_type") or status.get("review_decision_type")
    decision_options_ref = status.get("decision_options_ref") or status.get("review_decision_options_ref")
    waiting_human = (
        status.get("project_status") == "waiting-human"
        or run_status == "waiting-human"
        or decision_mode == "human-gated"
    )

    if waiting_human:
        decision_label = decision_type or "pending human-gated"
        decision_ref = decision_options_ref or f"{project_root}/review-state.json"
        if decision_type == "phase2-handoff" and status.get("next_experiment_action") == "phase2-ready":
            return (
                f"Ask Codex to review the pending Phase 2 handoff options in {decision_ref} and wait "
                f"for operator choice before starting Phase 2."
            )
        return (
            f"Ask Codex to inspect the pending {decision_label} decision in {decision_ref}, summarize "
            f"the options, and do not auto-resume the run."
        )

    if current_run_id and run_status in {"running", "paused"}:
        step_name = status.get("current_step_name") or "the recorded step"
        if status.get("resume_safe") is False:
            return (
                f"Ask Codex to inspect {project_root}/review-state.json for run {current_run_id}, "
                f"explain whether resuming from {step_name} is safe, and do not continue execution "
                f"until the safety check is explicit."
            )
        return (
            f"Ask Codex to inspect {project_root}/review-state.json and resume run "
            f"{current_run_id} safely from {step_name} before starting any new branch."
        )

    if status.get("next_experiment_action") == "phase2-ready":
        return (
            f"Ask Codex to verify the evidence in {project_root}/experiment-memory.md and "
            f"start the approved Phase 2 workflow."
        )

    if status.get("phase") == "phase0" or not status.get("active_idea_id"):
        if not status.get("brief_ready", True):
            missing = ", ".join(status.get("brief_missing_fields", [])) or "required intake fields"
            return (
                f"Ask Codex to inspect {project_root}/project-brief.md, identify the missing intake "
                f"fields ({missing}), and help complete the brief before starting Phase 1 bootstrap."
            )
        return (
            f"Ask Codex to read {project_root}/project-brief.md and begin the Phase 1 bootstrap "
            f"(intake mode selection, literature review, and first idea candidate generation)."
        )

    next_action = status.get("next_action") or "inspect canonical state and proceed conservatively"
    return (
        f"Ask Codex to open {project_root}/STATE.md and {project_root}/experiment-memory.md, "
        f"then continue from the recorded next action: {next_action}."
    )
