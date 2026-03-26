---
name: overnight
description: Use for long-running Phase 1 or Phase 2 orchestration when the project needs recoverable checkpointing, strong autonomy, and clean pause/resume behavior through canonical run state.
---

# Overnight

## Overview

Run the research system for an extended stretch without turning the orchestrator into a hidden owner of scientific truth.

`overnight` is a run controller. It owns checkpointing, sequencing, pause/resume, and run summaries. It does not own experiment verdicts, archive narratives, or reusable memory.

## When to Use

Use when:

- you want Phase 1 or Phase 2 work to continue across multiple steps autonomously
- the project needs a recoverable `review-state.json`
- a previous run must resume after interruption or context compaction

Do not use when:

- the project lacks canonical state files
- the goal is only to resolve a human-gated decision manually without creating or maintaining run-state checkpoints
- the requested flow would require `overnight` to invent scientific state that belongs to another skill

## Read / Write Contract

### Read

- `projects/<slug>/project-brief.md`
- `projects/<slug>/STATE.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/review-state.json` when present
- `docs/policies/overnight-policy.md`

### Write

- `projects/<slug>/review-state.json`
- run-lifecycle fields in `projects/<slug>/STATE.md`

### Must Not Write

- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/results.tsv`
- `projects/<slug>/plans/<idea>/anchor.md`
- `projects/<slug>/decision-tree.md`
- `projects/<slug>/archive/archive-<experiment_id>.md`
- `projects/<slug>/archive/artifacts/<experiment_id>/...`
- `memory/*`
- `projects/<slug>/workspace/dashboard-data.json`

## Required Input Checks

Before starting or resuming, verify:

- `project-brief.md` exists and contains a usable intake configuration
- `STATE.md` exists and is structurally readable
- `experiment-memory.md` exists and is structurally readable
- `review-state.json` is valid JSON if resuming

Additional mode checks:

- `phase1` start:
  - allowed when the project is in `phase0` or `phase1`
- `phase2` start:
  - allowed only when the active experiment line is `phase2-ready` or the project is already in `phase2`
- `resume`:
  - allowed only when the stored run is internally consistent and safe to resume
- fresh run collision check:
  - if `STATE.md.current_run_id` points to a different unfinished run, stop and use `resume` or close that run canonically first

If these checks fail, stop and report the exact missing contract or invalid state.

## Protocol

### 1. Determine Run Mode

Supported modes:

- `phase1`
- `phase2`
- `resume`

For `phase1`, treat `project-brief.md` as the canonical source of intake configuration.

Do not rely on an ephemeral topic string as the only source of truth.

For `phase2`, verify Phase 2 readiness before taking ownership.

For `resume`, load the existing run and reuse its `run_id`.

### 2. Load Canonical Run Context

Read:

- `project-brief.md` for intake mode, autonomy preferences, escalation triggers, and environment constraints
- `STATE.md` for current phase, current run, decision posture, human attention state, and next action
- `experiment-memory.md` for the active line snapshot and latest validation posture
- `review-state.json` when present for prior step history and paused-run context

Stop if canonical files disagree in a way that makes the next step unsafe to choose.

### 3. Initialize Or Validate Run State

For a new run, create `review-state.json` only when there is no different unfinished active run.

Then write a valid Run State record with:

- `run_id`
- `run_type`
- `project_id`
- `phase`
- `target_id`
- `status: running`
- `started_at`
- `updated_at`
- `finished_at: null`
- `current_step_index`
- `current_step_name`
- `resume_safe`
- `blocking_reason`
- `decision_mode`
- `human_attention`
- `decision_type`
- `decision_options_ref`
- `decision_options`
- empty or existing `errors`, `warnings`, and `artifacts`
- `summary`
- `steps[]`

For a resumed run:

- verify only one step is `in-progress` at most
- verify completed steps remain coherent
- verify any paused decision still matches canonical state through `decision_options_ref`

Then update `STATE.md` run-lifecycle fields:

- set `current_run_id`
- set `project_status` to `running` unless canonical state already requires `waiting-human`
- refresh `decision_mode`, `human_attention`, `risk_level`, `blockers`, and `last_updated`
- set `phase: phase2` only when a Phase 2 run actually begins

Maintain the invariant that `STATE.md.current_run_id` matches `review-state.json.run_id` while the run remains active or paused.

Do not change `active_idea_id`, `active_branch_id`, or experiment verdict state here.

### 4. Select The Next Approved Step

Choose one approved next step at a time.

#### Phase 1 Bootstrap Segment

If no active experiment line exists yet, use the approved bootstrap sequence:

1. `literature-review`
2. `idea-creator`
3. `novelty-check`
4. `experiment-plan`
5. `anchor-wrapper`

Drive this sequence from `project-brief.md` intake mode:

- `direction-search`
- `seed-papers`

Keep each step checkpointed separately in `review-state.json`.

#### Phase 1 Validation Loop

After an active line exists, route from canonical state:

- `anchor-wrapper` when the current line already has a concrete experiment plan but no bound anchor yet
- `run-experiment` when the line is ready for first execution, rerun, or bounded tweak
- `analyze-results` when new result evidence exists without current structured analysis
- `drift-detector` when current analysis exists but drift for the latest evidence is missing or stale
- `judge` when drift is `consistent` and `next_experiment_action` is `judge-ready`
- `experiment-plan` when judge has already set `next_experiment_action: branch`, canonical posture still allows bounded autonomous branching, and the current idea-scoped plan slot is safe to reuse
- `archive` when judge has already set `next_experiment_action: archive` and the project is not human-gated

If the latest canonical posture is `phase2-ready`, finish the Phase 1 run as a handoff-ready completion instead of faking a Phase 2 start.

#### Phase 2 Execution

Do not inline paper workflow details here.

Use:

- `phase2-publish`

as the approved delegated publication workflow.

### 5. Check Human-Gated Posture Before Continuing

Before executing the selected step, inspect `STATE.md`.

If canonical posture is:

- `decision_mode: human-gated`

then:

1. resolve `STATE.md.decision_options_ref`
2. if `STATE.md.decision_type` is non-null, `STATE.md.human_attention` is `async-review` or `required-now`, and the canonical decision artifact is readable and exposes at least one option:
   - set run `status: waiting-human`
   - mirror `decision_type`
   - mirror `decision_options_ref`
   - mirror non-empty `decision_options`
   - update `review-state.json`
   - stop cleanly
3. if `decision_type` is missing, `human_attention` is invalid, or the canonical decision artifact is missing, unreadable, or optionless:
   - set run `status: paused`
   - set `blocking_reason` to the exact decision-mirror contract failure
   - set `resume_safe: false`
   - update `review-state.json`
   - stop and report the contract gap

Do not clear or rewrite the canonical decision in `STATE.md`.

If canonical posture instead shows:

- `human_attention: async-review`
- or `human_attention: required-now`

without a `human-gated` decision artifact, then:

1. set run `status: paused`
2. set `blocking_reason` from canonical steering state
3. set `resume_safe: false` only if the blocker makes safe continuation ambiguous
4. update `review-state.json`
5. stop cleanly without inventing decision options

### 6. Execute The Step And Checkpoint It

For the selected step:

1. append a step record if it is new
2. mark that step `in-progress`
3. update `current_step_index`, `current_step_name`, and `updated_at`
4. invoke the selected downstream skill
5. on success:
   - mark the step `completed`
   - record `finished_at`
   - refresh `output_ref` or `notes` when the downstream artifact is clear
6. re-read `STATE.md` and `experiment-memory.md`

Keep `review-state.json` structurally valid after every checkpoint.

### 7. Continue, Pause, Or Finish

After each step:

- continue automatically when canonical posture remains `auto` or `auto-report` and the next step is policy-approved
- pause when canonical posture becomes human-gated
- fail or pause when required inputs for the next core step are missing
- complete the Phase 1 run when the project is handoff-ready for Phase 2
- complete the Phase 2 run when the delegated publishing workflow reaches a stable terminal checkpoint

### 8. Error Handling

Treat core scientific and governance steps as non-skippable.

Core steps include:

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

If a core step cannot run safely:

- record the exact blocker in `errors`
- set the step to `failed` or leave it `in-progress` only if safe re-run semantics are explicit
- set `resume_safe` conservatively
- stop instead of silently skipping forward

Optional best-effort projection or notification work may be recorded as warnings only if canonical state is already correct.

### 9. Resume Rules

On resume:

- continue from the first unfinished safe step
- preserve completed-step history
- re-run an `in-progress` step only when it is clearly safe to do so
- stop if prior side effects are ambiguous and human review is needed first

If a mirrored decision was pending, do not auto-clear it.

Resume only after canonical decision posture has been resolved or intentionally resumed into the same paused context.

### 10. Finalize The Run

When the run reaches `completed`, `failed`, or `cancelled`:

- finalize `review-state.json`
- set `finished_at`
- write a compact `summary`
- refresh `updated_at`
- clear `STATE.md.current_run_id`
- preserve the last scientific posture written by the most recent sub-skill

When the run reaches a stable `waiting-human` boundary:

- checkpoint `review-state.json` in paused form
- leave `finished_at: null`
- keep `STATE.md.current_run_id`
- keep mirrored decision options only while that paused run remains active

If a meaningful terminal or paused session boundary was reached, invoke `reflect`.

Do not use `reflect` as hidden mid-run housekeeping.

## Failure Handling

Stop without writing further run progress if:

- the run mode is invalid for the canonical project posture
- canonical files are missing or structurally unreadable
- the next step would require `overnight` to invent scientific state
- a supposed resume target has ambiguous side effects

When stopping, report the exact missing file, invalid field, or ownership conflict.

## Self-Check

- [ ] Read only canonical run-routing inputs plus `docs/policies/overnight-policy.md`
- [ ] Wrote only `review-state.json` and run-lifecycle fields in `STATE.md`
- [ ] Used the approved Phase 1 bootstrap segment only until an active line existed
- [ ] Routed validation one approved step at a time from canonical state
- [ ] Paused cleanly on `human-gated` posture and mirrored decision options without taking ownership of them
- [ ] Delegated publication execution to `phase2-publish`
- [ ] Refused to skip core scientific or governance steps silently
- [ ] Finalized the run and invoked `reflect` only at a stable run boundary
