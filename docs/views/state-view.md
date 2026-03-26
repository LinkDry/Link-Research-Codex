# `STATE.md` Target Structure

## Purpose

`projects/<slug>/STATE.md` is the compact operator-facing view of Project State.

Its job is to answer, at a glance:

- where the project is
- what branch is currently primary
- what should happen next
- whether human attention is actually needed

## Owner Object

- Project State

## Canonical Role

`STATE.md` is the canonical persisted summary of current project steering state.

It may reference:

- `experiment-memory.md`
- `review-state.json`
- `decision-tree.md`

But it must not duplicate their full contents.

`decision_options_ref` should point to the canonical decision artifact for the current unresolved choice, while `review-state.json` only mirrors that choice during an active paused run.

`current_run_id` should point to the active `review-state.json.run_id` while a run is active or paused, and should be cleared when no active run remains.

If `decision_mode` is `human-gated`, `decision_type` and `decision_options_ref` must be populated, and `human_attention` must not remain `none`.

## Target Layout

```md
# Project State

## Identity
- project_id:
- project_title:
- last_updated:

## Steering
- phase:
- project_status:
- active_idea_id:
- active_branch_id:
- current_run_id:
- next_action:
- last_completed_skill:

## Decision Posture
- decision_mode:
- human_attention:
- decision_type:
- decision_options_ref:

## Risk
- risk_level:
- blockers:

## Refs
- experiment_memory_path:
- review_state_path:
- decision_tree_path:
```

## Field Mapping

| Line | Source Field |
|------|--------------|
| `project_id` | `project_id` |
| `project_title` | `project_title` |
| `last_updated` | `last_updated` |
| `phase` | `phase` |
| `project_status` | `project_status` |
| `active_idea_id` | `active_idea_id` |
| `active_branch_id` | `active_branch_id` |
| `current_run_id` | `current_run_id` |
| `next_action` | `next_action` |
| `last_completed_skill` | `last_completed_skill` |
| `decision_mode` | `decision_mode` |
| `human_attention` | `human_attention` |
| `decision_type` | `decision_type` |
| `decision_options_ref` | `decision_options_ref` |
| `risk_level` | `risk_level` |
| `blockers` | `blockers` |

The `Refs` section is derived from known project paths and is not treated as additional Project State schema.

## Formatting Rules

- keep the file short and scannable
- prefer one-line scalar values
- represent empty lists as `[]`
- if `decision_type` or `decision_options_ref` is absent, use `null`
- do not embed paragraphs of explanation

## Content That Does Not Belong Here

- judge history
- drift history
- raw metrics
- full branch comparison tables
- long lessons learned
- paper-writing detail

## Update Triggers

Update `STATE.md` when:

- phase changes
- primary branch changes
- run status meaningfully changes
- next action changes
- human attention state changes
- blockers or risk level change

Keep `phase: phase1` after a Phase 1 PASS until a Phase 2 workflow actually begins.
