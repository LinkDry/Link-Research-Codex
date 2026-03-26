# `analysis-report.json` Evidence Contract

## Purpose

`analysis-report.json` is the structured post-analysis artifact for one evaluated result group.

It exists so downstream skills such as `drift-detector` and `judge` can consume analysis output as explicit evidence instead of depending on freeform prose alone.

## Canonical Location

Recommended path:

- `projects/<slug>/workspace/results/<result-group-id>/analysis-report.json`

`latest_analysis_ref` in canonical state should normally point to this artifact.

## Relationship to Canonical State

`analysis-report.json` is a secondary evidence artifact owned by Experiment State.

It is not a replacement for:

- `experiment-memory.md`
- `results.tsv`

Instead:

- `results.tsv` records the ledger rows
- `analysis-report.json` interprets those rows
- `experiment-memory.md` stores the compact current-state summary and refs

## Required JSON Shape

```json
{
  "analysis_id": "analysis-001",
  "project_id": "proj-001",
  "experiment_id": "exp-001",
  "idea_id": "idea-001",
  "branch_id": "branch-main",
  "run_id": "run-001",
  "result_group_id": "rg-001",
  "generated_at": "2026-03-24T23:00:00+08:00",
  "summary": "Short interpretation of what the result means.",
  "primary_findings": [
    "Finding 1",
    "Finding 2"
  ],
  "metric_interpretation": [
    {
      "metric_name": "macro_f1",
      "observed_value": 0.74,
      "comparison_target": "baseline-a",
      "interpretation": "Improved over baseline but still below anchor target."
    }
  ],
  "evidence_gaps": [
    "Only one seed was run."
  ],
  "anomalies": [
    "Validation variance was higher than expected."
  ],
  "recommended_next_action": "tweak-mutable-vars",
  "referenced_results": [
    "results.tsv#rg-001"
  ],
  "referenced_artifacts": [
    "projects/demo/workspace/results/rg-001/config-snapshot.json"
  ]
}
```

## Required Fields

- `analysis_id`
- `project_id`
- `experiment_id`
- `idea_id`
- `branch_id`
- `run_id`
- `result_group_id`
- `generated_at`
- `summary`
- `primary_findings`
- `metric_interpretation`
- `evidence_gaps`
- `recommended_next_action`
- `referenced_results`

## Rules

1. The artifact must refer back to concrete results rows or result groups.
2. `recommended_next_action` is advisory evidence, not canonical state by itself.
3. If anomalies materially affect trust in the run, they must be listed explicitly.
4. The analysis artifact must remain machine-parseable JSON.

## Content That Does Not Belong Here

- live project steering fields
- hidden branch decisions
- retrospective lessons learned
- silent edits to results data
