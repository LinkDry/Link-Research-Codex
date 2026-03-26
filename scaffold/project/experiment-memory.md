# Experiment Memory

## Active Line Snapshot
| Field | Value |
|------|-------|
| experiment_id | null |
| idea_id | null |
| branch_id | null |
| parent_branch_id | null |
| status | planned |
| anchor_path | null |
| anchor_version | null |
| iteration_count | 0 |
| latest_result_ref | null |
| latest_analysis_ref | null |
| latest_drift_score | null |
| latest_drift_decision | null |
| latest_judge_verdict | null |
| judge_confidence | null |
| latest_judge_report_ref | null |
| success_criteria_status | unknown |
| archive_recommended | false |
| human_review_required | false |
| next_experiment_action | wait-human |
| last_updated | 2026-03-24T00:00:00+08:00 |

## Anchor Summary
- locked_anchor_path: null
- anchor_claim_summary: No anchor has been locked yet.
- anchor_constraints: Define the first anchor before running experiments.

## Latest Evidence Summary
- latest_result_ref: null
- latest_analysis_ref: null
- primary_signal_summary: No evidence recorded yet.
- open_risks: ["No active anchor", "No evaluation evidence", "No drift review"]

## Iteration History
| iteration | run_id | result_ref | analysis_ref | status | notes |
|-----------|--------|------------|--------------|--------|-------|
| - | - | - | - | - | No iterations recorded yet. |

## Drift and Judge Log
| timestamp | iteration | drift_score | drift_decision | judge_verdict | next_action | human_review_required |
|-----------|-----------|-------------|----------------|---------------|-------------|-----------------------|
| - | - | - | - | - | - | - |

## Branch Outcomes
| experiment_id | idea_id | branch_id | parent_branch_id | final_status | final_judge_verdict | final_drift_score | archive_ref |
|---------------|---------|-----------|------------------|--------------|---------------------|-------------------|-------------|
| - | - | - | - | - | - | - | - |

## Latest Analysis Block
- summary: No analysis has been produced yet.
- evidence_gaps: ["Run the first experiment", "Produce the first structured analysis", "Evaluate drift against the anchor"]
- recommended_next_action: Lock an anchor and execute the first validation run.
