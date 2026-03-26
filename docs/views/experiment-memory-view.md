# `experiment-memory.md` Target Structure

## Purpose

`projects/<slug>/experiment-memory.md` is the human-facing view of Experiment State.

It should show:

- the active experiment line
- the bound anchor and latest evidence
- drift and judge outcomes
- structured history across iterations and branches

## Owner Object

- Experiment State

## Canonical Role

`experiment-memory.md` is the canonical persisted summary of the current active experiment line.

It may reference:

- `results.tsv`
- `plans/<idea>/anchor.md`
- `decision-tree.md`
- `archive/*.md`

Raw result detail stays in `results.tsv` and linked artifacts.

## Target Layout

```md
# Experiment Memory

## Active Line Snapshot
| Field | Value |
|------|-------|
| experiment_id | |
| idea_id | |
| branch_id | |
| parent_branch_id | |
| status | |
| anchor_path | |
| anchor_version | |
| iteration_count | |
| latest_result_ref | |
| latest_analysis_ref | |
| latest_drift_score | |
| latest_drift_decision | |
| latest_judge_verdict | |
| judge_confidence | |
| latest_judge_report_ref | |
| success_criteria_status | |
| archive_recommended | |
| human_review_required | |
| next_experiment_action | |
| last_updated | |

## Anchor Summary
- locked_anchor_path:
- anchor_claim_summary:
- anchor_constraints:

## Latest Evidence Summary
- latest_result_ref:
- latest_analysis_ref:
- primary_signal_summary:
- open_risks:

## Iteration History
| iteration | run_id | result_ref | analysis_ref | status | notes |

## Drift and Judge Log
| timestamp | iteration | drift_score | drift_decision | judge_verdict | next_action | human_review_required |

## Branch Outcomes
| experiment_id | idea_id | branch_id | parent_branch_id | final_status | final_judge_verdict | final_drift_score | archive_ref |

## Latest Analysis Block
- summary:
- evidence_gaps:
- recommended_next_action:
```

## Field Mapping

The `Active Line Snapshot` section should directly mirror these Experiment State fields:

- `experiment_id`
- `idea_id`
- `branch_id`
- `parent_branch_id`
- `status`
- `anchor_path`
- `anchor_version`
- `iteration_count`
- `latest_result_ref`
- `latest_analysis_ref`
- `latest_drift_score`
- `latest_drift_decision`
- `latest_judge_verdict`
- `judge_confidence`
- `latest_judge_report_ref`
- `success_criteria_status`
- `archive_recommended`
- `human_review_required`
- `next_experiment_action`
- `last_updated`

## Section Rules

### Anchor Summary

- summarize the locked claim in 1-3 bullets
- do not silently mutate the claim to fit later evidence
- if the claim materially changes, create a new anchor version or branch

### Latest Evidence Summary

- summarize only the most decision-relevant evidence
- always point back to `latest_result_ref` and `latest_analysis_ref`
- do not embed raw metric dumps already present elsewhere
- prefer `latest_analysis_ref` to resolve to a structured analysis artifact such as `analysis-report.json`

### Iteration History

- one row per completed iteration
- include the run that produced the evidence
- keep notes short and operational

### Drift and Judge Log

- one row per major review point
- drift and judge entries may share the same iteration
- if human review is required, mark it explicitly in the row

### Branch Outcomes

- one row per completed or archived branch line
- this is where final verdict and final drift score belong
- archived branches should point to a project archive record

## Content That Does Not Belong Here

- raw training logs
- full evaluation tables copied from artifacts
- global lessons learned
- detailed run-step orchestration

## Update Triggers

Update `experiment-memory.md` when:

- a new anchor is locked
- an iteration completes
- analysis completes
- drift status changes
- judge verdict changes
- judge report ref changes
- a branch is merged, abandoned, or archived
