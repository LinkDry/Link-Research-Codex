# `review-state.json` Target Structure

## Purpose

`projects/<slug>/review-state.json` is the machine-oriented view of Run State.

It exists to make long-running execution recoverable, resumable, and inspectable.

## Owner Object

- Run State

## Canonical Role

`review-state.json` is the canonical persisted controller for an active or resumable run.

If a run exists, this file should be sufficient to answer:

- what the run is doing now
- what already finished
- whether it can resume
- whether a human decision is pending

When a scientific decision is paused for review, this file may mirror the current option set, but it is not the canonical owner of branch-governance history or verdict rationale.

## Target JSON Skeleton

```json
{
  "run_id": "run-001",
  "run_type": "phase1-overnight",
  "project_id": "proj-001",
  "phase": "phase1",
  "target_id": "exp-001",
  "status": "running",
  "started_at": "2026-03-24T20:00:00+08:00",
  "updated_at": "2026-03-24T20:30:00+08:00",
  "finished_at": null,
  "current_step_index": 3,
  "current_step_name": "drift-detector",
  "resume_safe": true,
  "decision_mode": "auto-report",
  "human_attention": "none",
  "blocking_reason": null,
  "decision_type": null,
  "decision_options_ref": null,
  "decision_options": [],
  "artifacts": [],
  "errors": [],
  "warnings": [],
  "summary": null,
  "steps": [
    {
      "index": 1,
      "name": "anchor-wrapper",
      "status": "completed",
      "started_at": "2026-03-24T20:00:00+08:00",
      "finished_at": "2026-03-24T20:05:00+08:00",
      "input_ref": "projects/demo/STATE.md",
      "output_ref": "projects/demo/plans/idea-001/anchor.md",
      "notes": "Anchor locked successfully."
    }
  ]
}
```

## Required Top-Level Fields

- `run_id`
- `run_type`
- `project_id`
- `phase`
- `target_id`
- `status`
- `started_at`
- `updated_at`
- `current_step_index`
- `current_step_name`
- `resume_safe`
- `decision_mode`
- `human_attention`
- `errors`
- `warnings`
- `steps`

## Optional Top-Level Fields

- `finished_at`
- `blocking_reason`
- `decision_type`
- `decision_options_ref`
- `decision_options`
- `artifacts`
- `summary`

## `decision_options[]` Structure

When `status` is `waiting-human`, each decision option should contain:

- `option_id`
- `label`
- `summary`
- `pros`
- `cons`
- `recommended`
- `expected_effect`

Prefer mirroring these options from the canonical decision artifact referenced by `STATE.md.decision_options_ref` when such an artifact exists.

This keeps human escalation structured instead of burying the choice inside prose.

## `steps[]` Structure

Each step object should contain:

- `index`
- `name`
- `status`
- `started_at`
- `finished_at`
- `input_ref`
- `output_ref`
- `notes`

The orchestrator may append new step objects as the next approved action becomes concrete.

It should not rewrite completed steps into a different history after the fact.

## State Rules

1. Only one `steps[]` entry may be `in-progress`.
2. If `status` is `waiting-human`, then:
   - `decision_type` must be non-null
   - `decision_options_ref` must be non-null
   - `decision_options` must not be empty
   - `human_attention` must be `required-now` or `async-review`
3. If `status` is `waiting-human`, `decision_options` should mirror the current canonical decision posture rather than invent a second source of truth.
4. If `status` is `completed`, `failed`, or `cancelled`, then `finished_at` must be set.
5. `updated_at` must change on every meaningful run-state transition.
6. This file must remain valid JSON with no comments.

## Current Run Pointer Rule

While the run remains active or paused, `STATE.md.current_run_id` should match `review-state.json.run_id`.

## Content That Does Not Belong Here

- long scientific analysis paragraphs
- full lessons learned
- copied result tables
- hidden decision context that only exists in prose elsewhere

## Update Triggers

Update `review-state.json` when:

- a run starts
- the next approved step is appended
- a step changes status
- a pause or resume occurs
- a human decision is requested or resolved
- errors, warnings, or artifacts change
- the run finishes or fails
