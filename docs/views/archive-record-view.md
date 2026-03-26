# `archive-<experiment_id>.md` Archive Record Contract

## Purpose

`archive-<experiment_id>.md` is the project-local closure record for one archived experiment line.

It exists to preserve full case context without forcing active state or global memory to carry historical detail forever.

## Canonical Location

Recommended path:

- `projects/<slug>/archive/archive-<experiment_id>.md`

## Relationship to Canonical State

This archive record is historical context, not active state.

It should point back to:

- `results.tsv`
- `anchor.md` or a stable archived snapshot of it
- `analysis-report.json`
- `judge-report.json`
- `decision-tree.md`

## Target Layout

```md
# Archive Record

## Identity
- archive_id:
- project_id:
- experiment_id:
- idea_id:
- branch_id:
- parent_branch_id:
- archived_at:
- archive_reason:
- archive_trigger_ref:

## Final Outcome
- final_status:
- final_judge_verdict:
- final_drift_decision:
- final_drift_score:
- total_iterations:
- success_criteria_status:

## Locked Claim Context
- anchor_path:
- anchor_version:
- claim_summary:
- plan_ref:

## Evidence Summary
- result_refs:
- analysis_refs:
- judge_report_ref:
- artifact_bundle_path:
- evidence_limitations:

## Failure Analysis
- failure_class:
- why_it_failed:
- what_would_need_to_change:
- key_takeaway:
- when_to_warn_again:

## Workspace Preservation
| item_path | handling | archive_path | notes |
|-----------|----------|--------------|-------|

## Memory Promotion
- lesson_ref:
- failure_library_ref:
- similarity_tags:
```

## Rules

1. This record should summarize and reference evidence rather than copying whole ledgers.
2. `archive_trigger_ref` should point to the verdict or human decision that caused closure.
3. `artifact_bundle_path` should resolve to the preserved archive artifact directory when one exists.
4. `Workspace Preservation` must record unresolved or ambiguous files instead of hiding them.
5. This file must remain human-readable and structurally consistent enough for later extraction.
6. `lesson_ref` and `failure_library_ref` should point to concrete inserted memory row refs or stable IDs, not dangling template anchors.
7. When live idea-scoped `anchor.md` or `experiment-plan.md` files may later be reused, `anchor_path` and `plan_ref` should resolve to archived snapshot copies inside the artifact bundle.
8. For early-abandonment or pre-anchor closures, `anchor_path`, `anchor_version`, `claim_summary`, and `plan_ref` may be `null`; do not invent missing locked-claim context.
