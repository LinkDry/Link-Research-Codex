# `config-snapshot.json` Evidence Contract

## Purpose

`config-snapshot.json` is the machine-comparable record of the concrete run configuration for one evaluation event.

It exists so `drift-detector` can compare what actually ran against the anchor's mutable and immutable boundaries without heuristic workspace scans.

## Canonical Location

Recommended path:

- `projects/<slug>/workspace/results/<result-group-id>/config-snapshot.json`

`results.tsv.artifact_path` should normally point to the artifact directory that contains this file.

## Relationship to Canonical State

`config-snapshot.json` is a secondary evidence artifact owned by Experiment State.

It does not replace:

- `anchor.md`
- `results.tsv`
- `experiment-memory.md`

Instead:

- `anchor.md` defines what is allowed
- `config-snapshot.json` records what actually ran

## Required JSON Shape

```json
{
  "snapshot_id": "cfg-001",
  "project_id": "proj-001",
  "experiment_id": "exp-001",
  "idea_id": "idea-001",
  "branch_id": "branch-main",
  "run_id": "run-001",
  "result_group_id": "rg-001",
  "captured_at": "2026-03-24T22:30:00+08:00",
  "method_under_test": "adapter-finetune-v1",
  "mutable_values": {
    "learning_rate": 0.0001,
    "batch_size": 16
  },
  "immutable_values": {
    "base_model": "model-a",
    "loss_function": "contrastive-margin"
  },
  "data_config": {
    "dataset": "demo-benchmark",
    "split": "dev"
  },
  "environment": {
    "execution_target": "local-wsl"
  },
  "notes": [
    "Seed fixed at 42."
  ]
}
```

## Required Fields

- `snapshot_id`
- `project_id`
- `experiment_id`
- `idea_id`
- `branch_id`
- `run_id`
- `result_group_id`
- `captured_at`
- `method_under_test`
- `mutable_values`
- `immutable_values`

## Rules

1. Every key used for immutable-boundary comparison must appear in `immutable_values`.
2. Mutable settings that may legally drift across iterations should appear in `mutable_values`.
3. The snapshot must describe what actually ran, not what was intended to run.
4. The file must remain machine-parseable JSON.

## Content That Does Not Belong Here

- judge verdicts
- drift scores
- freeform session summaries
- retrospective lessons learned
