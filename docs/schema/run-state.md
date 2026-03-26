# Run State Schema

## Purpose

Run State tracks one recoverable execution instance.

Examples:

- `overnight phase1`
- `overnight phase2`
- long review loops
- resumed execution after interruption

It answers:

- what run is active
- what step is currently executing
- what already completed
- why the run paused or failed
- whether the run can safely resume

## Non-Goals

Run State does not store:

- project-wide research history
- experiment scientific interpretation
- cross-project lessons
- full raw result ledgers

## Primary File View

- `projects/<slug>/review-state.json`

## Required Fields

| Field | Type | Description | Primary Consumer |
|------|------|-------------|------------------|
| `run_id` | id | stable run identity | all layers |
| `run_type` | enum | execution mode | Codex, dashboard |
| `project_id` | id | owning project | all layers |
| `phase` | enum | phase covered by this run | Codex |
| `target_id` | id/null | main target idea, paper, or experiment | Codex |
| `status` | enum | current run lifecycle status | all layers |
| `started_at` | timestamp | run start time | dashboard |
| `updated_at` | timestamp | latest status update | dashboard |
| `current_step_index` | integer | active step index | Codex |
| `current_step_name` | string | active step name | operator |
| `steps` | array | structured list of run steps | Codex, dashboard |
| `resume_safe` | boolean | whether resuming is allowed | Codex |
| `decision_mode` | enum | current decision handling mode | Codex |
| `human_attention` | enum | whether operator attention is needed | dashboard |
| `errors` | array | recorded run errors | Codex |
| `warnings` | array | recorded run warnings | Codex |

## Optional Fields

| Field | Type | Description |
|------|------|-------------|
| `finished_at` | timestamp/null | finish time when closed |
| `blocking_reason` | string/null | current blocking reason |
| `decision_type` | enum/null | current decision type |
| `decision_options_ref` | ref/null | canonical ref for the mirrored active decision while paused |
| `decision_options` | array | structured options mirrored for operator review while the run is paused |
| `artifacts` | array | run-generated artifact refs |
| `summary` | string/null | compact run summary |

## Enums

### `run_type`

- `phase1-overnight`
- `phase2-overnight`
- `review-loop`
- `manual-resume`
- `support`

### `phase`

- `phase0`
- `phase1`
- `phase2`
- `cross-phase`

### `status`

- `pending`
- `running`
- `paused`
- `waiting-human`
- `failed`
- `cancelled`
- `completed`

### `step.status`

- `pending`
- `in-progress`
- `completed`
- `skipped`
- `failed`
- `cancelled`
- `budget-skipped`

### `decision_mode`

- `auto`
- `auto-report`
- `human-gated`

### `human_attention`

- `none`
- `async-review`
- `required-now`

### `decision_type`

- `branch-decision`
- `phase2-handoff`
- `archive-review`
- `integrity-review`
- `resource-review`

## Step Structure

Each `steps[]` entry should contain:

- `index`
- `name`
- `status`
- `started_at`
- `finished_at`
- `input_ref`
- `output_ref`
- `notes`

The controller may append new step entries as routing decisions become concrete.

Completed step records should remain stable history rather than being rewritten into a different plan.

## Resume Rule

A run is resumable only if:

- state file is internally consistent
- current step is known
- completed steps are clearly marked
- any in-progress step can be safely re-run
- any mirrored paused decision still points to the same canonical decision ref

## Decision Mirror Rule

If a run is waiting on a human decision, `decision_options` may mirror the active canonical options referenced by `STATE.md.decision_options_ref`.

Run State does not own branch-governance history or verdict rationale; it only carries the execution-time pause state.

When `status` is `waiting-human`:

- `decision_type` must be non-null
- `decision_options_ref` must match `STATE.md.decision_options_ref`
- `decision_options` must be non-empty
- `human_attention` must be `async-review` or `required-now`

When the canonical decision posture clears or changes, the mirrored `decision_options_ref` and `decision_options` in Run State should be cleared or refreshed to match.

## Current Run Pointer Rule

While a run remains active in one of these statuses:

- `pending`
- `running`
- `paused`
- `waiting-human`

`STATE.md.current_run_id` should match `review-state.json.run_id`.

When the run reaches a terminal status and no paused active run remains, `STATE.md.current_run_id` should be cleared.

## View Design Rule

`review-state.json` should remain machine-oriented and compactly parseable.

Do not replace structured fields with long freeform text.

Dynamic routing is allowed, but the file must always remain structurally valid after each checkpoint.
