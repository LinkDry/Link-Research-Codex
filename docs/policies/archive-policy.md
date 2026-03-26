# Archive Policy

## Purpose

This document is the single authoritative policy for closing an experiment line in Link-Research.

It exists to keep archival safe, traceable, and reusable without letting cleanup logic destroy evidence or blur project-local history with global memory.

## Archive Unit

The archive unit is one experiment line:

- `experiment_id`
- `idea_id`
- `branch_id`

Archive does not mean "delete an idea from history."

It means "close this line, preserve its evidence, and promote the reusable lesson."

## Archive Triggers

Archive may run when:

- `judge` has already issued `archive`
- a human explicitly requests closure of a line
- an early-abandonment case is being closed conservatively

## Preservation Rules

### Canonical Evidence Must Survive

Archive must never rewrite or delete:

- `projects/<slug>/results.tsv`
- `projects/<slug>/plans/<idea>/anchor.md`
- canonical result or verdict refs already recorded in active state

If the current idea-scoped `anchor.md` or `experiment-plan.md` slot may later be reused, archive
should snapshot those files into `projects/<slug>/archive/artifacts/<experiment_id>/` and point the
archive record at the stable archived copies rather than the live slot paths.

If the line was abandoned before an anchor or attributable experiment plan existed, archive should
keep the locked-claim fields in the archive record as `null` and describe the incomplete state in
the evidence or failure sections rather than inventing claim context.

### Project-Local Case Record

Archive must create:

- `projects/<slug>/archive/archive-<experiment_id>.md`

This is the full project-local closure record for the line.

### Workspace Handling Rule

For workspace artifacts attributable to the archived line:

1. move or snapshot them into:
   - `projects/<slug>/archive/artifacts/<experiment_id>/`
2. if ownership is ambiguous, do not auto-delete
3. instead, record the unresolved paths in the archive record

Automatic deletion is not the default archival behavior in this harness.

## Global Memory Promotion Rule

Every archive should promote:

1. one reusable lesson into `memory/lessons-learned.md`
2. one failure-library entry into `memory/failure-library.md` when a reusable failure class or warning signal is identifiable

Global memory should point back to the project-local archive record rather than duplicating the full case.

## Active-State Cleanup Rule

Archive must update active state conservatively.

### Experiment State

Archive must:

- append a `Branch Outcomes` row with `final_status: archived`
- record the `archive_ref`
- preserve prior iteration and drift/judge history

If the archived line is the current active line, reset the active snapshot to these neutral defaults unless another line has already been explicitly activated:

- `experiment_id: null`
- `idea_id: null`
- `branch_id: null`
- `parent_branch_id: null`
- `status: planned`
- `anchor_path: null`
- `anchor_version: null`
- `iteration_count: 0`
- `latest_result_ref: null`
- `latest_analysis_ref: null`
- `latest_drift_score: null`
- `latest_drift_decision: null`
- `latest_judge_verdict: null`
- `judge_confidence: null`
- `latest_judge_report_ref: null`
- `success_criteria_status: unknown`
- `archive_recommended: false`
- `human_review_required: false`
- `next_experiment_action: wait-human`

Reset the compact summary blocks to these exact neutral defaults as well:

- `locked_anchor_path: null`
- `anchor_claim_summary: No anchor has been locked yet.`
- `anchor_constraints: Define the first anchor before running experiments.`
- `latest_result_ref: null`
- `latest_analysis_ref: null`
- `primary_signal_summary: No evidence recorded yet.`
- `open_risks: ["No active anchor", "No evaluation evidence", "No drift review"]`
- `summary: No analysis has been produced yet.`
- `evidence_gaps: ["Run the first experiment", "Produce the first structured analysis", "Evaluate drift against the anchor"]`
- `recommended_next_action: Lock an anchor and execute the first validation run.`

### Branch Governance

Archive must update `decision-tree.md` to reflect that the line is no longer active.

Allowed changes:

- remove or mark the archived branch out of `Active Branch Register`
- append a `Branch Outcomes` row with the archive ref
- clear `primary_branch_id` if the primary line was archived and no replacement was explicitly activated

### Project State

If the archived line was active:

- clear `active_branch_id`
- clear `active_idea_id` only if no remaining active branch for that idea is designated
- keep `current_run_id` unchanged because Run State owns run lifecycle
- clear `decision_type` and `decision_options_ref` unless a next decision remains pending
- set `next_action` to activate a remaining branch or resume ideation
- choose `idle`, `running`, or `waiting-human` conservatively based on whether a next line is already known

Archive must not silently activate a different branch unless that activation decision has already been made elsewhere.

## Non-Goals

Archive should not:

- rewrite judge history
- mutate anchors to better fit the failure narrative
- update `_index.md` projections
- hide uncertain cleanup behind deletion

## Run-State Boundary

Archive does not write `review-state.json`.

If archive happens during an active run, the orchestrator that owns Run State must react afterward by updating `review-state.json` based on the new project posture.
