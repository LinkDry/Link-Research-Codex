# Overnight Policy

## Purpose

This document is the single authoritative policy for `overnight`.

`overnight` is the run controller for long-running autonomous or semi-autonomous execution. It exists to keep runs recoverable, bounded, and honest without turning run state into a hidden source of scientific truth.

## Scope

`overnight` governs:

- run initialization
- checkpointing
- pause and resume
- approved step sequencing
- mirroring human-decision options into `review-state.json` while paused

`overnight` does not govern:

- scientific verdict logic
- drift logic
- archive closure details
- reusable memory promotion
- dashboard projection contents

## Ownership Boundary

### `overnight` Owns

- `projects/<slug>/review-state.json`
- run-lifecycle fields in `projects/<slug>/STATE.md`

### `overnight` Must Not Write Directly

- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/results.tsv`
- `projects/<slug>/plans/<idea>/anchor.md`
- `projects/<slug>/decision-tree.md`
- project archive records or artifact bundles
- `memory/*`
- `projects/<slug>/workspace/dashboard-data.json`

Those belong to sub-skills or derived projections.

## Run Modes

### `phase1`

Use when the project should autonomously progress through idea intake, experiment setup, validation, and judge/archive checkpoints.

### `phase2`

Use only when:

- the active experiment line is `phase2-ready`
- or the project is already in `phase2`

### `resume`

Use only when `review-state.json` is structurally valid and the current step is safely resumable or safely re-runnable.

## Active Run Collision Rule

Do not start a fresh `phase1` or `phase2` run if `STATE.md.current_run_id` already points to a different unfinished run.

In that case:

- use `resume`
- or explicitly close the old run canonically first

`overnight` must not overwrite an unrelated active `review-state.json` just to make progress.

## Phase 1 Routing Model

Phase 1 has two parts in the current architecture.

### 1. Bootstrap Segment

When no active experiment line exists yet, `overnight` may use a fixed approved bootstrap mini-sequence because the system does not yet have a separate canonical Idea State object.

Approved bootstrap sequence:

1. `literature-review`
2. `idea-creator`
3. `novelty-check`
4. `experiment-plan`
5. `anchor-wrapper`

Input source:

- `project-brief.md`

Use:

- `direction-search` to drive open literature discovery
- `seed-papers` to constrain the search around the provided papers

The bootstrap sequence is still checkpointed step-by-step in `review-state.json`.

### 2. Validation Loop

Once an active experiment line exists, `overnight` should route one approved next step at a time from canonical state.

#### Validation Routing Table

| Canonical Condition | Next Step | Notes |
|---|---|---|
| active line is anchored and `next_experiment_action` is `run-first-experiment`, `rerun`, or `tweak-mutable-vars` | `run-experiment` | bounded autonomous continuation is allowed when project posture remains auto or auto-report |
| active line has a concrete experiment plan but no bound anchor yet | `anchor-wrapper` | this covers both fresh setup and bounded branch continuation after `experiment-plan` |
| `latest_result_ref` changed and the corresponding analysis is missing or stale | `analyze-results` | analysis must be regenerated before drift or judge |
| analysis exists for the latest result and drift for that result is missing or stale | `drift-detector` | drift owns the integrity gate |
| latest drift decision is `consistent` and `next_experiment_action` is `judge-ready` | `judge` | judge owns verdict, next action, and human-gating posture |
| judge leaves `next_experiment_action: branch` and the project remains auto or auto-report | `experiment-plan` | this starts the bounded branch handoff by creating the next branch plan before anchor lock, but only after judge has already confirmed the current idea-scoped plan slot is safe to reuse |
| judge leaves `next_experiment_action: archive` and the project is not human-gated | `archive` | archive is the conservative closure path |
| judge leaves `next_experiment_action: phase2-ready` | complete the Phase 1 run as handoff-ready | Phase 1 ends without flipping `STATE.md.phase` yet |

## Autonomy Rule

`overnight` should continue automatically when all of these are true:

- `STATE.md.decision_mode` is `auto` or `auto-report`
- `STATE.md.human_attention` is `none`
- the next step is already approved by policy
- no sub-skill has opened a pending human decision

This keeps automation strong for bounded reruns and conservative same-line iteration.

## Human-Gated Decision Rule

If canonical state shows:

- `decision_mode: human-gated`

then `overnight` must:

1. pause the run
2. mirror the active decision into `review-state.json`
3. leave the canonical decision posture in `STATE.md` and the referenced artifact untouched

`review-state.json` is a mirror during pause, not the source of truth for the decision itself.

To write a contract-valid `waiting-human` state:

- `STATE.md.decision_type` must be non-null
- `STATE.md.decision_options_ref` must be readable
- `STATE.md.human_attention` must be `async-review` or `required-now`
- at least one structured decision option must be mirrorable into `review-state.json`

If those conditions fail, do not write `waiting-human`.

Instead, stop with a run-state contract error and keep the blocker explicit.

## Attention Pause Rule

If canonical state does not open a human-gated decision but still sets:

- `human_attention: async-review`
- or `human_attention: required-now`

then `overnight` should:

- checkpoint the run as `paused`
- keep `STATE.md.current_run_id`
- record the blocking reason from canonical steering state
- stop without inventing decision options

## Phase 2 Delegation Rule

`overnight` must not inline a second copy of the publication workflow.

Instead:

- starting a Phase 2 run flips `STATE.md.phase` to `phase2`
- `overnight` delegates the actual publication work to `phase2-publish`
- the publishing workflow owns citation, writing, compile, and review-loop detail

This keeps `overnight` focused on run control rather than paper semantics.

## Error Rule

The harness is strict about core steps.

### Core Scientific Or Governance Steps

The following must not be silently skipped:

- `literature-review`
- `idea-creator`
- `novelty-check`
- `experiment-plan`
- `anchor-wrapper`
- `run-experiment`
- `analyze-results`
- `drift-detector`
- `judge`
- `archive`
- `phase2-publish`

If one of these cannot run safely:

- fail or pause the run
- record the exact blocker in `review-state.json`
- set `resume_safe` conservatively

### Optional Derived Refreshes

Best-effort projection or notification work may be downgraded to warnings if:

- canonical state is already correct
- the failure does not compromise scientific traceability

## Resume Rule

Resume is allowed only when:

- `review-state.json` is valid and internally consistent
- completed step records remain intact
- the current step is safely re-runnable or clearly unfinished
- any previously mirrored decision has been canonically resolved, or the run intentionally resumes into the same paused decision context

If step side effects are ambiguous, set `resume_safe: false` and stop for review.

## Completion Rule

When the run reaches a stable terminal checkpoint:

- finalize `review-state.json`
- clear `STATE.md.current_run_id`
- keep the last scientific posture owned by the most recent real sub-skill
- invoke `reflect` when a meaningful session boundary was reached

If the run is paused in `waiting-human`:

- keep `STATE.md.current_run_id`
- keep the run active but paused
- keep `review-state.json.decision_options_ref` aligned with `STATE.md.decision_options_ref`
- keep mirrored decision options only while that paused run remains active

### Phase 1 PASS Rule

After a passing Phase 1 run:

- keep `STATE.md.phase: phase1`
- end with handoff-ready posture

### Phase 2 Start Rule

`STATE.md.phase` changes to `phase2` only when the Phase 2 run actually starts and takes ownership.
