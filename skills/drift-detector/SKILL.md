---
name: drift-detector
description: Use after analysis is available for the active experiment line to check whether the run still matches the locked anchor before any judge verdict.
---

# Drift Detector

## Overview

Check whether the latest experiment evidence still matches the locked anchor.

This skill is the anti-goal-shift gate between running an experiment and judging whether the idea is working. It prevents the system from quietly changing the claim, the metric, or the core design and then pretending the evidence still supports the original idea.

## When to Use

Use when:

- an anchor is already bound in `experiment-memory.md`
- at least one result row exists in `results.tsv`
- `latest_analysis_ref` resolves to a structured `analysis-report.json`
- the relevant result artifact directory contains `config-snapshot.json`
- the active experiment line is ready to move toward judgment

Do not use when:

- there is no locked anchor
- results have not been recorded yet
- analysis has not been written yet

## Read / Write Contract

### Read

- `projects/<slug>/STATE.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/plans/<idea>/anchor.md`
- `projects/<slug>/results.tsv`
- `projects/<slug>/workspace/results/<result-group-id>/analysis-report.json` through `latest_analysis_ref` or `results.tsv.analysis_ref`
- `projects/<slug>/workspace/results/<result-group-id>/config-snapshot.json` through the active result rows' `artifact_path`

### Write

- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/STATE.md`

### Must Not Write

- `projects/<slug>/plans/<idea>/anchor.md`
- `projects/<slug>/results.tsv`
- `projects/<slug>/review-state.json`
- `memory/*`
- `projects/<slug>/workspace/dashboard-data.json`

## Required Evidence Checks

Before issuing any drift decision, verify all of the following exist:

- a bound `anchor_path`
- at least one result row for the active `experiment_id`
- a readable structured `analysis-report.json`
- a readable `config-snapshot.json`
- explicit immutable boundaries through `locked_invariants`
- explicit red lines in the anchor

If any are missing, stop and report the gap. Do not guess.

## Protocol

### 1. Load Active Context

Read:

- `STATE.md` for `project_id`, `phase`, `active_idea_id`, `active_branch_id`, and current steering posture
- `experiment-memory.md` for the active experiment snapshot, latest evidence refs, and anchor binding

Stop if:

- there is no active experiment line
- `anchor_path` is missing
- the line is not in a state where drift can be assessed

### 2. Load Locked Anchor

Read the bound anchor file from `anchor_path`.

Confirm the anchor contains:

- `claim`
- `primary_success_criteria`
- `allowed_mutations`
- `locked_invariants`
- `red_lines`
- `disconfirming_signals`
- `archive_if_true`

Stop if the anchor is incomplete. Report the exact missing section.

### 3. Load Current Evidence

Use `experiment-memory.md` plus `results.tsv` as the primary evidence source, then resolve the structured evidence artifacts those files point to.

Inspect:

- the latest result rows for the active `experiment_id`
- the referenced `analysis-report.json`
- the referenced `config-snapshot.json`

Do not scan the entire workspace as if it were canonical state.

### 4. Assess Drift

Score three dimensions on a 1-10 scale:

1. `hypothesis_alignment`
   - Is the current experiment still testing the locked claim?
2. `metric_alignment`
   - Are the recorded metrics, result interpretation, and evaluation target still aligned with `primary_success_criteria`?
3. `invariant_integrity`
   - Are all `locked_invariants` still intact when compared against `config-snapshot.json`?

Rules:

- if any locked invariant changed, force `anchor-violation`
- if any red line is triggered by current evidence, force `red-line`
- if any `archive_if_true` condition is triggered by current evidence, force `red-line`
- otherwise, compute a conservative overall score from the three dimensions

### 5. Choose Exactly One Drift Decision

Use exactly one of these decisions:

- `consistent`
- `drift-detected`
- `anchor-violation`
- `red-line`

Decision guidance:

- `consistent`
  - no invariant break
  - no red line trigger
  - score remains strong enough to proceed
- `drift-detected`
  - evidence is still related to the anchor, but alignment has slipped enough that automatic judgment should pause
- `anchor-violation`
  - any locked invariant changed
- `red-line`
  - any explicit stopping rule is triggered

### 6. Update Experiment State

Update `experiment-memory.md`:

- `latest_drift_score`
- `latest_drift_decision`
- `human_review_required`
- `next_experiment_action`
- `last_updated`

Append one row to `Drift and Judge Log` with:

- timestamp
- iteration
- drift_score
- drift_decision
- `judge_verdict` left blank or placeholder
- next action
- human review flag

Recommended next actions:

- `consistent` -> `wait-human` only if a separate strategic decision is pending; otherwise `judge-ready`
- `drift-detected` -> `wait-human`
- `anchor-violation` -> `wait-human`
- `red-line` -> `archive`

### 7. Update Project Steering State

Update `STATE.md` through canonical steering fields only:

- `project_status`
- `next_action`
- `decision_mode`
- `human_attention`
- `decision_type`
- `decision_options_ref`
- `risk_level`
- `last_completed_skill`
- `last_updated`

Recommended posture:

- `consistent`
  - `project_status: running`
  - `decision_mode: auto-report`
  - `human_attention: none`
  - clear `decision_type` and `decision_options_ref`
  - `next_action: proceed to judge`
- `drift-detected`
  - `project_status: blocked`
  - `decision_mode: auto-report`
  - `human_attention: async-review`
  - clear `decision_type` and `decision_options_ref`
  - `next_action: review drift and decide whether to correct or pivot`
- `anchor-violation`
  - `project_status: blocked`
  - `decision_mode: auto-report`
  - `human_attention: required-now`
  - clear `decision_type` and `decision_options_ref`
  - `next_action: inspect invariant violation and decide whether to revert, branch, or approve a new anchor path`
- `red-line`
  - `project_status: blocked`
  - `decision_mode: auto-report`
  - `human_attention: required-now`
  - clear `decision_type` and `decision_options_ref`
  - `next_action: review forced stop and likely archive`

## Optional Cross-Model Review

If Codex review is available through local Codex execution, you may request an advisory second opinion on the drift score.

Rules:

- treat the external review as advisory only, not canonical state
- do not let it silently overwrite the primary decision record
- if the models disagree materially, keep the more conservative operational posture and mention the disagreement in the user-facing output

## Failure Handling

Stop without writing if:

- `anchor_path` is missing
- no relevant results rows exist
- no structured `analysis-report.json` exists
- no `config-snapshot.json` exists
- `locked_invariants` or `red_lines` are missing from the anchor

When stopping, report the exact missing evidence or contract gap.

## Self-Check

- [ ] Read only canonical state plus explicitly referenced `analysis-report.json` and `config-snapshot.json` artifacts
- [ ] Wrote only `experiment-memory.md` and `STATE.md`
- [ ] Produced exactly one of the four allowed drift decisions
- [ ] Blocked automatic progression on invariant breaks or red-line triggers
- [ ] Did not mutate `anchor.md` or `results.tsv`
- [ ] Encoded the post-drift posture through canonical steering fields rather than freeform appended prose
