---
name: phase2-publish
description: Use for the approved Phase 2 publication workflow after a validated line reaches `phase2-ready`.
---

# Phase2 Publish

## Overview

Turn one validated Phase 1 line into a conservative publication package.

This skill is the approved publication workflow that `overnight` delegates to. It owns
publication artifacts under `projects/<slug>/papers/` plus the corresponding steering updates in
`STATE.md`. It does not rewrite scientific evidence, anchors, or run state.

## When to Use

Use when:

- `experiment-memory.md` shows `next_experiment_action: phase2-ready`
- or `STATE.md.phase` is already `phase2`
- the active line has a readable anchor and traceable evidence refs
- no active `phase2-handoff` decision remains in `STATE.md`

Do not use when:

- the active line has not passed Phase 1
- drift or verdict state is unresolved
- `STATE.md.decision_mode` is `human-gated`
- `STATE.md.decision_type` is `phase2-handoff`
- the required evidence refs cannot be resolved safely

## Read / Write Contract

### Read

- `projects/<slug>/STATE.md`
- `projects/<slug>/project-brief.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/plans/<idea>/anchor.md` through `anchor_path`
- `projects/<slug>/results.tsv`
- `projects/<slug>/workspace/results/<result-group-id>/analysis-report.json` through canonical refs
- `projects/<slug>/workspace/results/<result-group-id>/config-snapshot.json` through canonical refs
- `projects/<slug>/workspace/reviews/<experiment_id>/judge-report-<iteration>.json` through canonical refs
- existing files under `projects/<slug>/papers/drafts/`, `projects/<slug>/papers/reviews/`, and `projects/<slug>/papers/assets/` when resuming or revising

### Write

- `projects/<slug>/papers/drafts/paper-<experiment_id>.md`
- `projects/<slug>/papers/reviews/paper-<experiment_id>-review-round-<n>.md`
- `projects/<slug>/papers/assets/<experiment_id>/...`
- `projects/<slug>/STATE.md`

### Must Not Write

- `projects/<slug>/review-state.json`
- `projects/<slug>/results.tsv`
- `projects/<slug>/plans/<idea>/anchor.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/decision-tree.md`
- `memory/*`
- `projects/<slug>/workspace/dashboard-data.json`

## Required Gate Checks

Before doing publication work, verify all of the following:

- `latest_judge_verdict: pass`
- `next_experiment_action: phase2-ready`
- `STATE.md.decision_mode` is not `human-gated`
- `STATE.md.decision_type` is not `phase2-handoff`
- `anchor_path` is non-null and readable
- `latest_result_ref`, `latest_analysis_ref`, and `latest_judge_report_ref` are readable
- the linked `config-snapshot.json` can be resolved from the active evidence

If any gate fails, stop and report the exact missing contract. If a pending `phase2-handoff`
decision still exists, stop and report that operator handoff must be completed before starting
Phase 2.

## Protocol

### 1. Take Phase 2 Ownership

If this workflow is the component actually starting Phase 2 for a handoff-ready line:

- confirm `STATE.md` is not currently in `decision_mode: human-gated`
- confirm `STATE.md` does not carry `decision_type: phase2-handoff`

- update `STATE.md`
- set `phase: phase2`
- set `project_status: running`
- set `decision_mode: auto-report`
- set `human_attention: none`
- clear `decision_type` and `decision_options_ref`
- set `next_action: build the publication package for the validated line`

If `STATE.md.phase` is already `phase2`, keep the existing phase and just refresh the steering posture as needed.

### 2. Load Validated Line Context

Read:

- `STATE.md` for current phase, steering posture, and blockers
- `project-brief.md` for venue goals, scope limits, and integrity red lines
- `experiment-memory.md` for the active line snapshot
- the bound `anchor.md`
- `judge-report.json`
- the evidence refs that support the validated line

Derive a stable `paper_id` as `paper-<experiment_id>` unless the project already has a stronger paper naming rule.

### 3. Build A Claims-Evidence Map

Construct a conservative claims-evidence map from:

- the locked anchor claim
- the explicit success criteria that were judged as met
- the current result rows
- the current structured analysis

Rules:

- every paper claim must point to concrete result refs or analysis refs
- no new central claim may exceed the locked anchor
- limitations and caveats must remain visible

If the map cannot be made without stretching the evidence, stop and record a publication review note instead of forcing a draft.

### 4. Write Or Update The Draft

Write:

- `projects/<slug>/papers/drafts/paper-<experiment_id>.md`

The draft should include:

- title
- problem framing
- validated claim
- method summary tied to the anchor
- experiment and result summary tied to evidence refs
- limitations and failure boundaries
- next submission-facing checklist

Keep the draft evidence-traceable. Do not treat this file as canonical scientific state.

### 5. Optional Cross-Model Review

If Codex review is available through local Codex execution, you may request an advisory second opinion on:

- claims-evidence traceability in the current draft
- overclaim or framing drift relative to the locked anchor and judged evidence
- missing caveats, limitations, or methodology clarifications
- publication-time integrity risks that are easier to spot from a reviewer posture

Rules:

- treat the external review as advisory only
- do not let it rewrite canonical evidence or steering state on its own
- if disagreement is material, keep the more conservative publication posture
- record the outcome in the publication review note

### 6. Write A Publication Review Note

Write:

- `projects/<slug>/papers/reviews/paper-<experiment_id>-review-round-01.md`

Summarize:

- claims-evidence coverage
- unresolved writing gaps
- unresolved citation or bibliography gaps
- publication-time integrity risks
- cross-model review outcome when used
- whether the line is ready to continue drafting, blocked for human review, or ready for final packaging

Create additional `review-round-<n>` files for later passes instead of overwriting prior review history.

### 7. Package Attributable Assets

Create:

- `projects/<slug>/papers/assets/<experiment_id>/`

Copy or snapshot only attributable publication assets there, such as:

- exported figures or tables used by the draft
- cited analysis artifacts
- cited config snapshots
- a snapshot of the bound anchor for provenance

Do not move or rewrite canonical evidence files.

### 8. Handle Publication-Time Integrity Failures Conservatively

If publication review reveals a flaw that cannot be resolved by rewriting alone, such as:

- unsupported central claim
- missing critical evidence path
- irreconcilable methodology contradiction
- unresolved citation integrity problem that changes the paper's factual support

then:

- stop publication work
- keep existing Phase 1 evidence untouched
- write the blocking review note under `projects/<slug>/papers/reviews/`
- update `STATE.md` to a blocker posture:
  - keep `phase: phase2` only if a Phase 2 run already took ownership; otherwise keep the current phase
  - `project_status: blocked`
  - `decision_mode: auto-report`
  - `human_attention: required-now`
  - clear `decision_type` and `decision_options_ref`
  - `next_action: inspect the Phase 2 integrity review note and decide whether to revise framing or return to Phase 1`

Do not paper over the problem by weakening claims silently.

### 9. Finalize Steering State

If the publication package is in a good handoff state:

- update `STATE.md`
- keep `phase: phase2`
- set `project_status: completed` only when the current publication package is materially ready for external submission or operator handoff; otherwise keep `running`
- set `decision_mode: auto-report`
- set `human_attention: none`
- clear `decision_type` and `decision_options_ref`
- set `next_action` to review or submit the paper package
- set `last_completed_skill: phase2-publish`
- refresh `last_updated`

## Failure Handling

Stop without writing if:

- the line is not `phase2-ready`
- `STATE.md` is still `human-gated`
- `STATE.md.decision_type` is `phase2-handoff`
- required evidence refs cannot be resolved
- the anchor is missing
- the active line identity is ambiguous

When stopping, report the exact missing ref or contract conflict.

## Self-Check

- [ ] Confirmed the active line is `phase2-ready` before starting publication work
- [ ] Confirmed no active `decision_mode: human-gated` or `decision_type: phase2-handoff` gate remained before Phase 2 takeover
- [ ] Flipped `STATE.md.phase` to `phase2` when this workflow actually took ownership of a handoff-ready line
- [ ] Read only canonical project and experiment state plus referenced evidence artifacts
- [ ] Wrote only `papers/` outputs plus steering updates in `STATE.md`
- [ ] Did not mutate `results.tsv`, anchors, `experiment-memory.md`, `decision-tree.md`, or dashboard data
- [ ] Kept the draft evidence-traceable to the validated line
- [ ] Used blocker posture instead of silent overclaim when publication-time integrity failed
- [ ] Treated any cross-model review as advisory only
