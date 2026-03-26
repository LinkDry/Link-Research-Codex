---
name: experiment-plan
description: Use to create the canonical `experiment-plan.md` for either the first active line or a bounded branch continuation before anchor lock.
---

# Experiment Plan

## Overview

Create the concrete validation plan that `anchor-wrapper` can lock.

`experiment-plan` is the bridge from bootstrap ideation or branch continuation into canonical active Experiment State.

## When to Use

Use when:

- a selected idea is ready for the first active line
- or `judge` has already left `next_experiment_action: branch` and the idea-scoped plan slot is safe to reuse

Do not use when:

- no selected idea or branch target can be identified safely
- an active branch should continue without replanning
- the next move would require rewriting a locked anchor instead of planning a new line

## Read / Write Contract

### Read

- `projects/<slug>/project-brief.md`
- `projects/<slug>/STATE.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/decision-tree.md`
- `projects/<slug>/workspace/bootstrap/literature-review.md` when bootstrapping
- `projects/<slug>/workspace/bootstrap/idea-candidates.md` when bootstrapping
- `projects/<slug>/workspace/bootstrap/novelty-check.md` when bootstrapping
- `projects/<slug>/workspace/reviews/<experiment_id>/judge-report-<iteration>.json` through `latest_judge_report_ref` when branching
- `docs/views/experiment-plan-view.md`

### Write

- `projects/<slug>/plans/<idea>/experiment-plan.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/STATE.md`
- `projects/<slug>/decision-tree.md`

### Must Not Write

- `projects/<slug>/plans/<idea>/anchor.md`
- `projects/<slug>/results.tsv`
- `projects/<slug>/review-state.json`
- `memory/*`
- `projects/<slug>/workspace/dashboard-data.json`

## Required Input Checks

Before proceeding, verify:

- the target `idea_id` is known
- the planning mode is unambiguous: initial line or branch continuation
- the project brief constraints are readable
- the inputs are strong enough to populate all required `experiment-plan.md` sections

If the target line cannot be identified safely, stop and report the exact ambiguity.

## Protocol

### 1. Determine Planning Mode

If there is no active experiment line yet:

- use bootstrap inputs from `novelty-check.md`

If `judge` already recommended branching:

- read the latest `judge-report.json`
- confirm the current idea-scoped plan slot is safe to reuse under the existing path contract

### 2. Establish Line Identity

Define or confirm:

- `idea_id`
- `branch_id`
- `experiment_id`
- `parent_branch_id` when the line is a branch continuation

Use stable repo-safe IDs that remain short and human-readable.

### 3. Author The Plan

Write `projects/<slug>/plans/<idea>/experiment-plan.md` using the documented input contract.

The plan must include:

- falsifiable hypothesis
- quantitative success criteria
- experimental design
- mutable versus immutable variables
- red lines and disconfirming signals
- evidence plan
- open risks

Do not leave placeholder-level vagueness for `anchor-wrapper` to guess around later.

### 4. Optional Cross-Model Review

If Codex review is available through local Codex execution, you may request an advisory second opinion on:

- falsifiability of the hypothesis
- adequacy of baselines, metrics, and thresholds
- whether mutable versus immutable boundaries are drawn clearly
- confounders or execution risks that would make the plan hard to interpret
- whether the success criteria are strong enough to justify later anchor lock

Rules:

- treat the external review as advisory only
- revise the plan conservatively before anchor lock when the critique exposes a real planning gap
- if disagreement is material, keep the more conservative plan
- if no safe plan remains after review, stop without instantiating the active line

Record any adopted critique in `experiment-plan.md`.

### 5. Instantiate Or Refresh Active Experiment State

Update `experiment-memory.md`:

- set `experiment_id`
- set `idea_id`
- set `branch_id`
- set `parent_branch_id`
- set `status: planned`
- clear `anchor_path` and `anchor_version`
- reset latest result, analysis, drift, and judge refs for the new active line
- set `success_criteria_status: unknown`
- set `archive_recommended: false`
- set `human_review_required: false`
- set `next_experiment_action: wait-human`
- refresh the active snapshot, anchor summary, latest evidence summary, and `last_updated`

Preserve prior history tables and branch outcomes for older lines.

### 6. Update Branch Governance

Update `decision-tree.md`:

- set `Governance Snapshot.active_idea_id`
- set `Governance Snapshot.primary_branch_id`
- add or refresh the planned line in `Active Branch Register`
- append a `Decision Log` row when the plan came from a judged branch recommendation

Do not claim the anchor exists yet. This step establishes a planned active line, not a locked one.

### 7. Update Project Steering State

Update `STATE.md`:

- keep or set `phase: phase1`
- set `project_status: running`
- set `active_idea_id`
- set `active_branch_id`
- set `next_action: lock the anchor for the planned line`
- set `decision_mode: auto-report`
- set `human_attention: none`
- clear `decision_type` and `decision_options_ref`
- set `last_completed_skill: experiment-plan`
- refresh `last_updated`

## Failure Handling

Stop without writing if:

- no selected idea or safe branch target can be resolved
- required plan sections cannot be authored from the available evidence
- the request would require rewriting a locked anchor or silently reusing an unsafe same-idea slot
- external critique reveals an unresolved planning gap that makes anchor lock unsafe

When stopping, report the exact blocking contract issue.

## Self-Check

- [ ] Wrote a canonical `experiment-plan.md`
- [ ] Created or refreshed the active line in `experiment-memory.md`
- [ ] Updated `decision-tree.md` only to reflect a planned active branch, not a locked anchor
- [ ] Left `anchor.md`, `results.tsv`, `review-state.json`, and dashboard data untouched
- [ ] Preserved old history while making the new line explicit
- [ ] Treated any cross-model review as advisory only
