---
name: reflect
description: Use when a meaningful work session or run segment has ended and reusable lessons, capability gaps, or compact project-summary updates need to be captured without mutating judge, archive, or run-controller state.
---

# Reflect

## Overview

Summarize the session and preserve only what should survive it.

`reflect` is intentionally narrow: it extracts reusable lessons, normalizes capability gaps, and refreshes the compact project summary. It is not a maintenance dispatcher or a hidden governance writer.

## When to Use

Use when:

- a meaningful session boundary has been reached
- an overnight or multi-step run finished a checkpoint
- new reusable lessons, blockers, or capability gaps may have emerged

Do not use when:

- a run is still actively in progress with no clear checkpoint
- the goal is to repair run state, judge state, or archive state directly

## Read / Write Contract

### Read

- `projects/<slug>/STATE.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/project-brief.md`
- `projects/<slug>/review-state.json` when present
- `memory/lessons-learned.md`
- relevant recent archive refs when they materially inform the session summary
- `docs/policies/reflect-policy.md`

### Write

- `memory/lessons-learned.md`
- selected compact summary fields in `projects/<slug>/STATE.md`

### Must Not Write

- `projects/<slug>/review-state.json`
- `projects/<slug>/project-brief.md`
- `projects/<slug>/results.tsv`
- anchors, judge reports, or archive records
- `memory/failure-library.md`
- `projects/<slug>/workspace/dashboard-data.json`

## Required Input Checks

Before reflecting, verify:

- the project has readable `STATE.md`
- there is enough recent state change or run context to summarize meaningfully
- `memory/lessons-learned.md` exists and can be updated structurally

If the session context is too ambiguous to reconstruct safely, stop and report that gap instead of fabricating a narrative.

## Protocol

### 1. Load Session Context

Read:

- `STATE.md` for current steering posture
- `experiment-memory.md` for the latest experiment changes
- `project-brief.md` for project goals and operator preferences
- `review-state.json` when present for step history, warnings, and run summary
- `memory/lessons-learned.md` to avoid duplicates and update existing gaps

Read recent archive refs only when they are part of what changed this session.

### 2. Reconstruct the Session Summary

Build a concise session summary answering:

- what changed
- what decisions were made
- what evidence or artifacts were produced
- what blockers or surprises emerged
- what the most likely next action is

This summary is primarily output for the operator, not a new owned file.

### 3. Extract Reusable Lessons

Add a new lesson only when at least one of these is true:

- the pattern is likely to recur
- the mistake would be expensive to repeat
- the success pattern is reusable
- the lesson materially changes how future sessions should operate

Append lessons to `memory/lessons-learned.md` `Recent Lessons` with:

- `lesson_id`
- `date`
- `scope`
- `project_id`
- `idea_id`
- `branch_id`
- `source_type: session-reflection`
- `category`
- `polarity`
- `summary`
- `source_ref`
- `evidence_ref`
- `reusable`
- `similarity_tags`

If no reusable lesson emerged, say so in the output rather than inventing filler rows.

### 4. Normalize Capability Gaps

Update `memory/lessons-learned.md` `Capability Gaps` when the session exposed a missing capability or recurring blocker.

Allowed gap types:

- `tool-gap`
- `doc-gap`
- `constraint-gap`
- `data-gap`
- `skill-gap`

For existing gaps:

- update status when resolved
- avoid duplicate near-identical rows

### 5. Queue Pattern Promotion When Needed

When the same pattern appears repeatedly, add a `Promotion Queue` row instead of directly editing governance docs or the failure library.

This queue should point back to the relevant lesson refs and explain why promotion is warranted.

### 6. Refresh Compact Project Summary

Update `STATE.md` only within the allowed summary fields:

- `next_action`
- `blockers`
- `risk_level`
- `last_completed_skill: reflect`
- `last_updated`

Do not use `reflect` to change:

- `phase`
- `project_status`
- `active_idea_id`
- `active_branch_id`
- `current_run_id`
- `decision_mode`
- `human_attention`
- `decision_type`
- `decision_options_ref`

Those belong to the skills or orchestrators that own the underlying state transitions.

### 7. Final Output

Report:

- the session summary
- new lessons added, if any
- capability gaps added or updated, if any
- whether any promotion-queue item was created
- the compact next action now reflected in `STATE.md`

If housekeeping is needed, mention it explicitly. Do not trigger hidden maintenance flows here.

## Failure Handling

Stop without writing if:

- `STATE.md` is missing
- `memory/lessons-learned.md` is unreadable or structurally corrupted
- there is not enough context to tell what actually happened

When stopping, report the exact missing context or file contract problem.

## Self-Check

- [ ] Read only canonical session context plus relevant archive refs
- [ ] Wrote only `memory/lessons-learned.md` and allowed summary fields in `STATE.md`
- [ ] Did not modify run state, project brief, judge artifacts, archive records, or dashboard data
- [ ] Added lessons only when they were reusable or actionable
- [ ] Updated capability gaps without duplicating resolved items
- [ ] Used Promotion Queue instead of directly mutating broader governance docs
- [ ] Did not trigger hidden downstream maintenance
