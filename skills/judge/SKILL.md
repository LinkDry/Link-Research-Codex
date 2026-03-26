---
name: judge
description: Use after drift is resolved and structured evidence exists to issue the Phase 1 verdict for the active experiment line.
---

# Judge

## Overview

Issue the Phase 1 verdict for the active experiment line.

This skill is the scientific gate between "we ran something" and "we now know what to do next." It must stay conservative, evidence-traceable, and governance-aware.

Detailed reasoning belongs in a structured `judge-report.json`; canonical verdict state belongs in `experiment-memory.md` and `STATE.md`.

## When to Use

Use when:

- the active line already has a locked anchor
- the latest drift decision is `consistent`
- `results.tsv` contains the latest evidence for the active line
- `latest_analysis_ref` resolves to a structured `analysis-report.json`
- the relevant result artifact directory contains `config-snapshot.json`

Do not use when:

- drift is unresolved
- no structured evidence exists yet
- the active line has no bound anchor

## Read / Write Contract

### Read

- `projects/<slug>/project-brief.md`
- `projects/<slug>/STATE.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/plans/<idea>/anchor.md`
- `projects/<slug>/results.tsv`
- `projects/<slug>/workspace/results/<result-group-id>/analysis-report.json` through `latest_analysis_ref` or the active result rows
- `projects/<slug>/workspace/results/<result-group-id>/config-snapshot.json` through the active result rows' `artifact_path`
- `projects/<slug>/decision-tree.md`
- `memory/lessons-learned.md`
- `docs/policies/judge-policy.md`

### Write

- `projects/<slug>/workspace/reviews/<experiment_id>/judge-report-<iteration>.json`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/STATE.md`
- `projects/<slug>/decision-tree.md` when branch governance posture changes

### Must Not Write

- `projects/<slug>/plans/<idea>/anchor.md`
- `projects/<slug>/results.tsv`
- `projects/<slug>/review-state.json`
- `memory/*`
- `projects/<slug>/workspace/dashboard-data.json`

## Required Evidence Checks

Before issuing any verdict, verify all of the following exist:

- an active `experiment_id`, `idea_id`, and `branch_id`
- a bound `anchor_path`
- a latest drift decision of `consistent`
- at least one active result row for the current experiment line
- a readable structured `analysis-report.json`
- a readable `config-snapshot.json`

If any of these are missing, stop and report the exact gap. Do not guess.

## Protocol

### 1. Load Active Context

Read:

- `STATE.md` for `phase`, `project_status`, `active_idea_id`, `active_branch_id`, `decision_mode`, and current steering posture
- `project-brief.md` for autonomy preferences, escalation conditions, and budget or ethics constraints
- `experiment-memory.md` for the active snapshot, prior verdicts, drift state, and current evidence refs
- `decision-tree.md` for active branch counts and prior governance decisions

Stop if:

- no active experiment line exists
- no active idea or branch is selected
- the line is not ready for judgment

### 2. Enforce the Drift Gate

Use `experiment-memory.md` as the canonical drift gate.

Rules:

- proceed only if `latest_drift_decision` is `consistent`
- if drift is `drift-detected` or `anchor-violation`, stop and point back to corrective handling
- if drift is `red-line`, stop and preserve the forced-stop posture already recorded by drift handling rather than issuing a normal verdict here

Do not override unresolved drift with optimistic judgment.

### 3. Load Locked Claim and Evidence

Read the locked anchor from `anchor_path` and inspect:

- `claim`
- `primary_success_criteria`
- `required_baselines`
- `locked_invariants`
- `red_lines`
- `disconfirming_signals`
- `archive_if_true`

Then inspect the current evidence bundle:

- all relevant rows from `results.tsv` for the active experiment line
- the resolved `analysis-report.json`
- the resolved `config-snapshot.json`
- similar lessons from `memory/lessons-learned.md` only as advisory context

Treat `results.tsv` plus structured artifacts as the evidence basis. Do not infer from unrelated workspace files.

### 4. Evaluate the Evidence Conservatively

Determine:

- `success_criteria_status`
  - `met`
  - `near-miss`
  - `unmet`
  - `invalidated`
- trend posture across iterations on the same branch
- whether evidence status or anomalies introduce material confounders
- whether the current setup still tests the locked claim rather than a softened version
- whether any `archive_if_true` stop condition is met by current evidence
- whether the evidence is trustworthy enough for a high-confidence verdict

Derive `judge_confidence` as:

- `high` when evidence is clear, aligned, and low-confounder
- `medium` when the direction is usable but confidence is reduced
- `low` when the evidence is noisy, underpowered, or materially ambiguous

### 5. Apply the Unified Judge Policy

Follow `docs/policies/judge-policy.md`.

Count consecutive non-pass verdicts on the same branch from the structured judge history in `experiment-memory.md`.

Rules:

- if the line clearly meets the gate with no unresolved material confounder, choose `pass`
- choose `tweak` only for bounded, same-line, mutable-variable iteration and only while below the forced-stop ceiling
- after 3 consecutive non-pass verdicts on the same branch, do not emit another same-line `tweak`
- when the current line should stop iterating directly but a bounded variant still exists, choose `rethink`
- when the line is no longer scientifically justified, choose `archive`
- if any `archive_if_true` condition from the bound anchor is clearly met by current evidence, do not choose `pass` or `tweak`; choose `archive`, or use human review only when the stop evidence itself is materially ambiguous

Map verdict to next action conservatively:

- `pass` -> `phase2-ready`
- `tweak` -> `tweak-mutable-vars`
- `rethink` -> `branch` or `wait-human`
- `archive` -> `archive`

Use `project-brief.md` plus branch-cap data from `decision-tree.md` to decide whether the next step is:

- `auto-report`
- or `human-gated`

Human gating is required when the next move is strategic, irreversible, ethics-sensitive, branch-cap constrained, or materially ambiguous.
Human gating is also required when the next branch plan or future anchor destination is ambiguous under the current idea-scoped path contract.
Under the current file mapping, `projects/<slug>/plans/<idea>/experiment-plan.md` and `anchor.md` behave as a single active branch slot per `idea_id`, so same-idea sibling branch activation should be treated as human-gated unless that slot is being safely repurposed after the prior line is closed or superseded.

### 6. Optional Cross-Model Review

If Codex review is available through local Codex execution, you may request an advisory second opinion.

Rules:

- keep the external review advisory only
- do not let it overwrite canonical state on its own
- if disagreement is material, keep the more conservative operational posture
- if disagreement makes the next action ambiguous, escalate to `human-gated`

Record the outcome in `judge-report.json`.

### 7. Write `judge-report.json`

Write:

- `projects/<slug>/workspace/reviews/<experiment_id>/judge-report-<iteration>.json`

Populate it using the documented schema:

- identity fields
- evidence refs
- drift gate status
- success criteria status
- verdict
- verdict confidence
- next action
- archive recommendation
- rationale summary
- confounders
- root causes
- suggested actions
- decision options when applicable
- cross-model review block

If a branch, archive, or Phase 2 handoff decision is pending, store the detailed options here.

### 8. Update Experiment State

Update `experiment-memory.md`:

- `status` -> `judged`
- `latest_judge_verdict`
- `judge_confidence`
- `latest_judge_report_ref`
- `success_criteria_status`
- `archive_recommended`
- `human_review_required`
- `next_experiment_action`
- `last_updated`

Append one row to `Drift and Judge Log` with:

- timestamp
- iteration
- latest drift score
- latest drift decision
- judge verdict
- next action
- human review flag

Refresh the compact evidence summary so the current verdict remains traceable to the active result and judge report refs.

Do not write final branch outcomes here unless the branch has actually been closed by a later action.

### 9. Update Project Steering State

Update `STATE.md` through canonical steering fields only.

Use these patterns:

- `pass`
  - if no human handoff choice remains, keep `phase: phase1`, set `project_status: running`, `decision_mode: auto-report`, `human_attention: none`, clear `decision_type` plus `decision_options_ref`, and set `next_action: start the approved Phase 2 workflow for the validated line`
  - if a real Phase 2 handoff choice is pending, keep `phase: phase1`, set `project_status: waiting-human`, `decision_mode: human-gated`, `human_attention: async-review` or `required-now`, set `decision_type: phase2-handoff`, set `decision_options_ref` to `projects/<slug>/workspace/reviews/<experiment_id>/judge-report-<iteration>.json#decision-options`, and set `next_action: review the Phase 2 handoff options before starting the workflow`
- `tweak`
  - `project_status: running`
  - `decision_mode: auto-report`
  - `human_attention: none`
  - clear `decision_type` and `decision_options_ref`
  - `next_action: run the next bounded tweak iteration`
- `rethink`
  - use autonomous `branch` only when the next branch plan and future anchor destination are unambiguous under the current path contract and the current idea-scoped plan or anchor slot can be safely reused; in that case keep `project_status: running`, `decision_mode: auto-report`, `human_attention: none`, clear `decision_type` plus `decision_options_ref`, and set `next_action: create the next bounded branch plan for the current line`
  - if human review is required or the path contract is ambiguous, use `project_status: waiting-human`, `decision_mode: human-gated`, `human_attention: async-review` or `required-now`, populate `decision_type: branch-decision`, set `decision_options_ref` to `projects/<slug>/workspace/reviews/<experiment_id>/judge-report-<iteration>.json#decision-options`, and set `next_action: review branch options for the current line`
- `archive`
  - if the archive decision is clear, use `project_status: running`, `decision_mode: auto-report`, `human_attention: none`, clear `decision_type` plus `decision_options_ref`, and set `next_action: run archive for the current line`
  - if archive needs operator confirmation, use `project_status: waiting-human`, `decision_mode: human-gated`, `human_attention: required-now`, `decision_type: archive-review`, `next_action: review archive decision for the current line`, and set `decision_options_ref` to `projects/<slug>/workspace/reviews/<experiment_id>/judge-report-<iteration>.json#decision-options`

Always update:

- `risk_level`
- `last_completed_skill: judge`
- `last_updated`

### 10. Update Branch Governance Only When Needed

Update `decision-tree.md` only if the verdict changes branch governance posture.

Allowed updates:

- append a summary row to `Decision Log`
- point `rationale_ref` to `projects/<slug>/workspace/reviews/<experiment_id>/judge-report-<iteration>.json`

Do not:

- create a new active branch entry before the branch actually exists
- rewrite prior branch history

## Failure Handling

Stop without writing if:

- there is no bound anchor
- drift is unresolved
- no relevant results rows exist
- no structured analysis artifact exists
- no config snapshot exists
- the success criteria cannot be traced to real evidence

When stopping, report the exact missing contract or evidence path.

## Self-Check

- [ ] Read only canonical state plus explicitly referenced `analysis-report.json` and `config-snapshot.json` artifacts
- [ ] Wrote only `judge-report.json`, `experiment-memory.md`, `STATE.md`, and `decision-tree.md` when governance changed
- [ ] Refused to issue a normal verdict when drift was unresolved
- [ ] Used the unified forced-stop policy and refused a fourth same-branch `tweak`
- [ ] Treated `archive_if_true` as a real forced-stop signal rather than a soft suggestion
- [ ] Kept PASS as `phase2-ready` without flipping `STATE.md.phase` to `phase2`
- [ ] Used `phase2-handoff` only for a real human-gated publication choice
- [ ] Stored detailed rationale and decision options in `judge-report.json`
- [ ] Treated cross-model review as advisory only
