---
name: run-experiment
description: Use when an anchored line is ready for a real evaluation event and the system needs to record attributable evidence without mutating the locked claim.
---

# Run Experiment

## Overview

Record one real evaluation event as canonical evidence.

`run-experiment` is the evidence-recording bridge between an anchored plan and downstream interpretation. It owns the append-only result rows and the concrete config snapshot for what actually ran.

## When to Use

Use when:

- the active line is anchored
- `next_experiment_action` is `run-first-experiment`, `rerun`, or `tweak-mutable-vars`
- the execution target can produce attributable metrics and a real config snapshot

Do not use when:

- there is no bound anchor
- the requested run would require changing locked invariants before execution
- the only available output is too ambiguous to record as evidence

## Read / Write Contract

### Read

- `projects/<slug>/project-brief.md`
- `projects/<slug>/STATE.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/plans/<idea>/anchor.md`
- `projects/<slug>/plans/<idea>/experiment-plan.md` when needed for mutable ranges or artifact expectations
- attributable files under `projects/<slug>/workspace/code/` and `projects/<slug>/workspace/data/` when relevant
- `docs/views/results-ledger-view.md`
- `docs/views/config-snapshot-view.md`

### Write

- `projects/<slug>/results.tsv`
- `projects/<slug>/workspace/results/<result-group-id>/config-snapshot.json`
- attributable files under `projects/<slug>/workspace/results/<result-group-id>/...`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/STATE.md`

### Must Not Write

- `projects/<slug>/plans/<idea>/anchor.md`
- `projects/<slug>/workspace/results/<result-group-id>/analysis-report.json`
- `projects/<slug>/review-state.json`
- `projects/<slug>/decision-tree.md`
- `memory/*`
- `projects/<slug>/workspace/dashboard-data.json`

## Required Input Checks

Before proceeding, verify:

- `anchor_path` is non-null and readable
- the active line identity is known
- the requested run stays within `allowed_mutations` and does not pre-break `locked_invariants`
- the execution environment named in `project-brief.md` is attributable and usable

If the run would break the anchor before execution, stop and report that violation instead of recording invalid evidence.

## Protocol

### 1. Load The Active Execution Envelope

Read:

- `project-brief.md` for the allowed execution environment and budget context
- `STATE.md` for current steering posture
- `experiment-memory.md` for the active line snapshot
- the bound `anchor.md`
- `experiment-plan.md` when the mutable-variable envelope needs clarification

### 2. Execute Or Capture The Evaluation Event

Run the anchored experiment in the declared environment, such as:

- local WSL
- SSH server

Only continue if the produced outputs are attributable to the active line and can be summarized honestly.

### 3. Create The Result Artifact Bundle

Define one stable `result_group_id` for this evaluation event and create:

- `projects/<slug>/workspace/results/<result-group-id>/`

Store:

- the required `config-snapshot.json`
- any attributable raw or summarized run files worth preserving with the result group

### 4. Write The Config Snapshot

Write `config-snapshot.json` using the documented evidence contract.

The snapshot must describe what actually ran, not what was intended to run.

### 5. Append Result Rows

Append one or more rows to `results.tsv`:

- one row per important metric
- one shared `result_group_id` for the evaluation event
- `artifact_path` pointing at the result-group directory
- `analysis_ref` left blank until analysis exists
- `evidence_status` set conservatively

Do not rewrite or delete old rows.

### 6. Update Experiment State

Update `experiment-memory.md`:

- set `status: running`
- increment `iteration_count`
- set `latest_result_ref` to the new result group
- clear `latest_analysis_ref`
- clear the current drift and judge snapshot fields for the new iteration
- set `success_criteria_status: unknown`
- set `archive_recommended: false`
- set `human_review_required: false`
- set `next_experiment_action: wait-human`
- refresh the latest evidence summary and `last_updated`

### 7. Update Project Steering State

Update `STATE.md`:

- keep `phase: phase1`
- set `project_status: running`
- set `next_action: analyze the latest result group before drift or judge`
- set `decision_mode: auto-report`
- set `human_attention: none`
- clear `decision_type` and `decision_options_ref`
- set `last_completed_skill: run-experiment`
- refresh `last_updated`

## Failure Handling

Stop without writing if:

- no valid anchor exists
- the result cannot be attributed safely to the active line
- no config snapshot can be recorded
- the run would require hidden mutation of locked invariants

When stopping, report the exact blocker.

## Self-Check

- [ ] Recorded only attributable evidence
- [ ] Appended rather than rewrote `results.tsv`
- [ ] Wrote a real `config-snapshot.json`
- [ ] Cleared stale analysis, drift, and judge snapshot fields for the new iteration
- [ ] Left the anchor and branch-governance files untouched
