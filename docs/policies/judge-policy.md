# Phase 1 Judge Policy

## Purpose

This document is the single authoritative policy for Phase 1 verdicting in Link-Research.

It exists to prevent V1-style drift where different skills or docs each invented their own archive threshold, Phase 2 gate, or branch-decision behavior.

## Scope

This policy governs:

- verdict eligibility for `judge`
- the unified forced-stop rule for repeated non-pass iterations
- what a PASS actually means for Phase 2 readiness
- how branch recommendations are recorded

## Verdict Preconditions

`judge` may issue a normal verdict only if all of the following are true:

1. the active experiment line has a bound `anchor_path`
2. the latest drift decision is `consistent`
3. the evidence path is traceable through:
   - `latest_result_ref`
   - `latest_analysis_ref`
   - referenced `config-snapshot.json`
4. no evidence row needed for the claim is marked `invalidated`

If these preconditions fail, `judge` must stop rather than manufacture a verdict.

## Verdict Meanings

### `pass`

Use only when:

- success criteria are met
- no unresolved material confounder invalidates the conclusion
- the active evidence still matches the locked anchor
- no `archive_if_true` stop condition from the bound anchor is met by current evidence

### `tweak`

Use only when:

- the line is still scientifically aligned with the anchor
- the outcome is a near miss or otherwise plausibly recoverable
- there is a bounded next iteration that changes only allowed mutable variables
- the branch has not hit the unified forced-stop ceiling

### `rethink`

Use when:

- the current line should not continue as another simple tweak
- the hypothesis framing, evaluation design, or branch strategy needs revision
- a bounded branch split may be the correct next move

`rethink` is the verdict used when the current branch should stop iterating directly but the idea family may still deserve a revised line.

### `archive`

Use when:

- the claim is contradicted strongly enough that no bounded next line is justified
- a red line or impossibility condition is reached
- an `archive_if_true` condition from the bound anchor is met by current evidence
- the branch has hit the forced-stop ceiling and no viable branch-worthy alternative remains

## Unified Forced-Stop Policy

This is the only authoritative repeated-failure rule in the current architecture.

### Counter Definition

Count consecutive non-pass verdicts on the same active branch:

- `tweak`
- `rethink`
- `archive`

Reset the counter only when:

- the branch receives `pass`
- a new branch becomes active

### Ceiling Rule

At `3` consecutive non-pass verdicts on the same branch:

1. `judge` must not emit another `tweak`
2. the branch must not continue as a same-line mutable-variable rerun
3. `judge` must choose one of these next postures:
   - `rethink` with `next_experiment_action: branch`
   - `rethink` with `next_experiment_action: wait-human`
   - `archive`

### Selection Guidance After Ceiling Hit

Choose `rethink` with `next_experiment_action: branch` only when:

- there is a concrete bounded alternative hypothesis or design variant
- branch count remains under the configured limit
- the move is not strategic, irreversible, or otherwise listed in `project-brief.md` escalation conditions
- the next branch plan and future anchor destination are unambiguous under the current path contract

Choose `rethink` with `next_experiment_action: wait-human` when:

- the best next step is strategic or costly
- branch-cap pressure is present
- model disagreement or evidence ambiguity makes autonomous branching unsafe
- the next branch would require ambiguous reuse of current idea-scoped plan or anchor artifacts

Choose `archive` when:

- the evidence contradicts the anchor strongly
- performance is stagnant or degrading with no bounded alternative
- a red line or impossibility signal applies
- a locked `archive_if_true` condition has clearly fired

### Current Branch Slot Rule

Current state is branch-aware, but the canonical `experiment-plan.md` and `anchor.md` files are still
idea-scoped paths.

Until branch-scoped plan and anchor paths exist, those files should be treated as a single active
branch slot per `idea_id`.

That means `judge` may recommend a new branch, but it must not leave an autonomous `branch` posture
when creating the next same-idea branch would require ambiguous reuse of the current slot.

## Phase 2 Readiness Contract

A `pass` verdict opens the Phase 2 gate, but it does not itself mean Phase 2 has already started.

### On PASS, `judge` must do this

In `experiment-memory.md`:

- set `latest_judge_verdict: pass`
- set `success_criteria_status: met`
- set `next_experiment_action: phase2-ready`
- set `archive_recommended: false`
- set `status: judged`

In `STATE.md`:

Use exactly one of these steering postures:

- non-blocking Phase 2 handoff
  - keep `phase: phase1`
  - set `project_status: running`
  - set `decision_mode: auto-report`
  - set `human_attention: none`
  - clear `decision_type` and `decision_options_ref`
  - set `next_action` to begin the approved Phase 2 planning or publishing workflow
- human-gated Phase 2 handoff
  - keep `phase: phase1`
  - set `project_status: waiting-human`
  - set `decision_mode: human-gated`
  - set `human_attention` to `async-review` or `required-now`
  - set `decision_type: phase2-handoff`
  - set `decision_options_ref` to `projects/<slug>/workspace/reviews/<experiment_id>/judge-report-<iteration>.json#decision-options`
  - set `next_action` to review the Phase 2 handoff options before starting the workflow

In both cases, `experiment-memory.md` still records `next_experiment_action: phase2-ready`.

### Phase Transition Rule

`STATE.md.phase` changes from `phase1` to `phase2` only when the Phase 2 orchestrator or publishing skill actually starts and takes ownership of the next run.

This avoids fake phase transitions caused by a verdict alone.

## Branch Decision Recording Contract

When `judge` recommends a split, promotion, or controlled stop:

1. `decision-tree.md` is the canonical governance summary
2. `judge-report.json` holds the detailed rationale and structured options
3. `STATE.md` exposes immediate operator posture through:
   - `decision_type`
   - `decision_options_ref`
   - `human_attention`
4. `review-state.json` may mirror those options only while an active run is paused

### Decision Tree Rule

`judge` may append a summary record to `decision-tree.md` `Decision Log`.

It must not update `Active Branch Register` as if the new branch already exists unless a later branch-creation action actually happens.

### Decision Ref Rule

If a branch, archive, or handoff decision is pending, `STATE.md.decision_options_ref` should point to `projects/<slug>/workspace/reviews/<experiment_id>/judge-report-<iteration>.json#decision-options`.

If `judge` leaves the project in a `human-gated` posture, it must also set:

- a non-null `decision_type`
- a non-null `decision_options_ref`
- `human_attention` to `async-review` or `required-now`

## Cross-Model Review Rule

Cross-model review is advisory evidence only.

It may:

- increase or decrease confidence
- trigger a more conservative posture
- escalate to human review when disagreement is material

It must not:

- overwrite canonical verdict state on its own
- create hidden state outside the documented write targets
