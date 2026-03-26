# `results.tsv` Target Structure

## Purpose

`projects/<slug>/results.tsv` is the append-only evidence ledger for Experiment State.

It provides a compact, parseable trail of what result was observed, for which branch and iteration, and from which run.

## Owner Object

- Experiment State

## Canonical Role

`results.tsv` is not the main experiment summary file.

Its job is narrower:

- preserve result evidence as ledger rows
- make later audit and comparison possible
- support traceable refs from `experiment-memory.md`, `judge`, and archive records

## Row Model

One row represents one summarized metric observation.

If a single evaluation run emits multiple important metrics:

- use one shared `result_group_id`
- write one row per metric

## Column Contract

| Column | Required | Description |
|--------|----------|-------------|
| `result_id` | yes | stable row identity |
| `result_group_id` | yes | groups rows from the same evaluation event |
| `supersedes_result_id` | no | points to a prior row when correcting earlier recording mistakes |
| `project_id` | yes | owning project |
| `experiment_id` | yes | owning experiment line |
| `idea_id` | yes | idea identity |
| `branch_id` | yes | branch identity |
| `iteration` | yes | iteration number for this result |
| `run_id` | yes | run that produced or recorded the result |
| `recorded_at` | yes | ISO 8601 timestamp |
| `result_kind` | yes | result category such as `eval`, `ablation`, `baseline`, `sanity-check` |
| `dataset` | no | dataset or benchmark name |
| `split` | no | split such as `train`, `dev`, `test` |
| `metric_name` | yes | metric label |
| `metric_value` | yes | observed value |
| `baseline_value` | no | comparison baseline value if relevant |
| `delta_value` | no | difference from baseline if relevant |
| `artifact_path` | no | path to the run artifact directory or primary evidence artifact |
| `analysis_ref` | no | pointer to the associated `analysis-report.json` or equivalent analysis artifact |
| `evidence_status` | yes | `valid`, `suspect`, or `invalidated` |
| `notes_ref` | no | pointer to extra notes or caveats |

## Header Example

```tsv
result_id	result_group_id	supersedes_result_id	project_id	experiment_id	idea_id	branch_id	iteration	run_id	recorded_at	result_kind	dataset	split	metric_name	metric_value	baseline_value	delta_value	artifact_path	analysis_ref	evidence_status	notes_ref
```

## Ledger Rules

1. Append only. Do not silently rewrite or delete old rows.
2. If a row was recorded incorrectly, add a new row and point `supersedes_result_id` at the old one.
3. `analysis_ref` should resolve to the analysis that interpreted the row or result group.
4. `evidence_status` must be downgraded if later audit finds contamination, misalignment, or invalid comparison.
5. `latest_result_ref` in `experiment-memory.md` should point to a `result_group_id` or a clearly defined row selector.
6. When possible, `artifact_path` should point to a result artifact directory that contains:
   - `analysis-report.json`
   - `config-snapshot.json`

## Content That Does Not Belong Here

- long freeform narratives
- branch decision rationale
- human choice menus
- lessons learned summaries

## Update Triggers

Append to `results.tsv` when:

- a benchmark evaluation completes
- a baseline comparison is recorded
- an ablation result is logged
- a prior result needs a traceable correction
