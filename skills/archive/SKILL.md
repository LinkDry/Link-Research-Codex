---
name: archive
description: Use when an experiment line must be closed after an archive verdict or explicit human request, and its evidence, artifacts, and reusable failure lessons need safe preservation.
---

# Archive

## Overview

Close one experiment line without losing what it taught us.

This skill preserves project-local case detail, promotes reusable lessons into global memory, and leaves active project state in a recoverable posture. It is move-or-snapshot oriented, not delete-first.

## When to Use

Use when:

- `judge` has already produced an `archive` verdict for a line
- a human explicitly asks to close a line conservatively
- an early-abandonment line needs to be preserved before the system moves on

Do not use when:

- the target line is still intended to continue
- the target line is ambiguous and cannot be identified safely

## Read / Write Contract

### Read

- `projects/<slug>/project-brief.md`
- `projects/<slug>/STATE.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/results.tsv`
- `projects/<slug>/decision-tree.md`
- `projects/<slug>/plans/<idea>/anchor.md` when present
- `projects/<slug>/plans/<idea>/experiment-plan.md` when present
- `projects/<slug>/workspace/results/<result-group-id>/analysis-report.json` through canonical refs when present
- `projects/<slug>/workspace/reviews/<experiment_id>/judge-report-<iteration>.json` through canonical refs when present
- attributable files under `projects/<slug>/workspace/`
- `memory/lessons-learned.md`
- `memory/failure-library.md`
- `docs/policies/archive-policy.md`

### Write

- `projects/<slug>/archive/archive-<experiment_id>.md`
- `projects/<slug>/archive/artifacts/<experiment_id>/...`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/STATE.md`
- `projects/<slug>/decision-tree.md`
- `memory/lessons-learned.md`
- `memory/failure-library.md`

### Must Not Write

- `projects/<slug>/results.tsv`
- `projects/<slug>/plans/<idea>/anchor.md`
- `projects/<slug>/plans/<idea>/experiment-plan.md`
- `projects/<slug>/review-state.json`
- `projects/<slug>/workspace/dashboard-data.json`
- any `_index.md`

## Required Input Checks

Before archiving, verify:

- the target `experiment_id`, `idea_id`, and `branch_id` are known
- the archive trigger is traceable to a judge verdict or explicit human request
- the current line can be matched to its evidence refs or clearly identified as early abandonment

If the line cannot be identified safely, stop and report the ambiguity.

## Protocol

### 1. Identify the Target Line

Use one of these sources:

- the active line in `experiment-memory.md` if it already carries `latest_judge_verdict: archive`
- a human-specified `experiment_id` or `branch_id`
- a prior archive recommendation already recorded in canonical state

Read:

- `STATE.md`
- `experiment-memory.md`
- `decision-tree.md`

Stop if more than one plausible line fits and no explicit target is available.

### 2. Gather Closure Evidence

Read the closure bundle for the target line:

- anchor path and anchor version when present
- experiment plan when present and still attributable to the archived line
- relevant `results.tsv` rows
- referenced `analysis-report.json`
- referenced `judge-report.json`
- branch governance context from `decision-tree.md`
- autonomy and risk constraints from `project-brief.md`
- attributable workspace artifacts

If results or analysis are sparse, classify the case as early abandonment or limited-evidence closure rather than inventing a stronger failure story.

### 3. Write the Project-Local Archive Record

Create:

- `projects/<slug>/archive/archive-<experiment_id>.md`

Use the archive record contract.

The record must include:

- identity and trigger refs
- final outcome summary
- locked claim context
- evidence refs
- failure analysis
- workspace preservation manifest
- memory-promotion refs once written

Prefer summaries plus refs over copying whole ledgers or whole anchor contents.
If the current idea-scoped `anchor.md` or `experiment-plan.md` slot may later be reused, point the
archive record to stable snapshot copies inside the archive artifact bundle instead of the live path.
If the line was abandoned before a locked claim or attributable experiment plan existed, keep
`anchor_path`, `anchor_version`, `claim_summary`, and `plan_ref` as `null` rather than inventing
missing claim context.

### 4. Preserve Workspace Artifacts Safely

Create:

- `projects/<slug>/archive/artifacts/<experiment_id>/`

For files confidently attributable to the archived line:

- move them into the archive artifact bundle
- or snapshot them if moving is risky or would destroy useful directory context

For the line's bound `anchor.md` and editable `experiment-plan.md`:

- keep the live canonical files untouched
- snapshot them into the artifact bundle when future slot reuse would make the live path historically ambiguous
- use those stable archived copies in `archive-<experiment_id>.md` when snapshots were taken

For files with ambiguous ownership:

- do not auto-delete
- leave them in place
- record them in the archive record's workspace preservation table as unresolved

Never delete canonical ledgers, anchors, or ambiguous evidence as part of archival.

### 5. Promote Global Memory

Append one reusable lesson to `memory/lessons-learned.md` using the existing table structure.

The lesson should include:

- stable IDs
- project, idea, and branch IDs
- `source_type: archive`
- concise summary
- archive record as `source_ref`
- concrete result or verdict refs as `evidence_ref`
- reusable tags

Append one structured failure entry to `memory/failure-library.md` when the failure class or warning pattern is identifiable.

At minimum, the failure entry should point back to:

- `archive_ref`
- evidence refs
- reusable warning signals

### 6. Update Experiment State

Update `experiment-memory.md`:

- preserve existing iteration history and drift/judge log
- append one `Branch Outcomes` row with:
  - `experiment_id`
  - `idea_id`
  - `branch_id`
  - `parent_branch_id`
  - `final_status: archived`
  - `final_judge_verdict`
  - `final_drift_score`
  - `archive_ref`

If the archived line is the currently active line and no replacement line has already been activated:

- reset the active snapshot and compact summary blocks to the exact neutral placeholder defaults defined in `docs/policies/archive-policy.md`
- keep the file recoverable and explicit about the lack of an active line

If the archived line is not the active line, do not disturb the current active snapshot.

### 7. Update Branch Governance

Update `decision-tree.md` to reflect the closure:

- remove or mark the archived branch out of `Active Branch Register`
- append one `Branch Outcomes` row with the archive ref
- clear `primary_branch_id` if the primary line was archived and no replacement is already designated

Do not silently activate a different branch here.

### 8. Update Project Steering State

Update `STATE.md` conservatively.

If the archived line was the active line:

- clear `active_branch_id`
- clear `active_idea_id` only if no remaining branch for that idea is already designated as primary
- keep `current_run_id` unchanged
- set `next_action` to either:
  - activate a remaining branch
  - or resume ideation
- set `project_status` to:
  - `running` only if a next line is already explicitly known
  - otherwise `idle` or `waiting-human`
- clear `decision_type` and `decision_options_ref` unless a next decision still remains pending

If the archived line was not the active line:

- keep current primary steering fields intact
- update only the parts needed to reflect that archival completed

Always update:

- `decision_mode`
- `human_attention`
- `risk_level`
- `last_completed_skill: archive`
- `last_updated`

### 9. Final Output

Report:

- archive record path
- preserved artifact bundle path if one exists
- whether the case was evidence-rich or early-abandonment
- lesson and failure-library refs
- what the next project action now is

## Failure Handling

Stop without writing if:

- the target line cannot be identified safely
- archive would require rewriting canonical evidence
- a claimed archive trigger cannot be traced to a verdict or explicit request

When stopping, report the exact ambiguity or contract conflict.

## Self-Check

- [ ] Archived one experiment line, not a vague idea blob
- [ ] Wrote `archive-<experiment_id>.md` with refs and failure analysis
- [ ] Preserved attributable workspace artifacts by move or snapshot
- [ ] Snapshotted live idea-scoped anchor or plan files when future slot reuse would otherwise make archive refs ambiguous
- [ ] Did not auto-delete ambiguous files
- [ ] Left `results.tsv` and anchors untouched
- [ ] Updated `experiment-memory.md` and `decision-tree.md` consistently
- [ ] Promoted reusable lessons into global memory with archive refs
- [ ] Left `current_run_id` and `review-state.json` ownership to the run orchestrator
- [ ] Did not touch `_index.md`, `review-state.json`, or dashboard projections
