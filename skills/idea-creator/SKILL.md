---
name: idea-creator
description: Use during Phase 1 bootstrap to turn the literature-review artifact into a bounded set of candidate ideas without silently activating canonical experiment state.
---

# Idea Creator

## Overview

Turn research context into a small set of candidate ideas that are concrete enough to validate.

`idea-creator` is still part of bootstrap. It creates durable candidate ideas, but it does not yet create the canonical active experiment line.

## When to Use

Use when:

- a current `literature-review.md` artifact exists
- the project needs a bounded candidate set for novelty filtering

Do not use when:

- bootstrap context is missing
- an active experiment line already exists and the task is not to restart bootstrap ideation

## Read / Write Contract

### Read

- `projects/<slug>/project-brief.md`
- `projects/<slug>/STATE.md`
- `projects/<slug>/workspace/bootstrap/literature-review.md`
- `memory/lessons-learned.md`
- `memory/failure-library.md`
- `docs/views/idea-candidates-view.md`

### Write

- `projects/<slug>/workspace/bootstrap/idea-candidates.md`
- `projects/<slug>/STATE.md`

### Must Not Write

- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/review-state.json`
- `projects/<slug>/results.tsv`
- `projects/<slug>/plans/<idea>/anchor.md`
- `projects/<slug>/decision-tree.md`
- `memory/*`
- `projects/<slug>/workspace/dashboard-data.json`

## Required Input Checks

Before proceeding, verify:

- `literature-review.md` exists and is structurally readable
- the literature artifact exposes at least one plausible opportunity zone
- the project brief's integrity red lines and baseline constraints are readable

If the literature artifact is too weak to support ideation safely, stop and report that gap instead of inventing candidates.

## Protocol

### 1. Load Bootstrap Inputs

Read:

- `project-brief.md`
- `STATE.md`
- `workspace/bootstrap/literature-review.md`
- relevant lessons or failure patterns that could constrain ideation

### 2. Generate A Bounded Candidate Set

Create between 2 and 5 candidate ideas.

Each candidate should include:

- a stable repo-safe `idea_id` such as `idea-001`
- a short title
- a falsifiable claim summary
- a novelty basis tied to the literature review
- a plausible validation shape
- key failure signals or red-flag risks
- source refs

If one idea seems strongest, mark it as recommended, but keep the set bounded and comparative.

### 3. Write The Candidate Artifact

Write `projects/<slug>/workspace/bootstrap/idea-candidates.md` using the documented bootstrap contract.

Also preserve:

- branch seeds or later variation hooks
- clearly deferred ideas worth revisiting later

### 4. Update Project Steering State

Update `STATE.md` conservatively:

- keep `phase: phase1`
- keep `project_status: running`
- keep `active_idea_id: null`
- keep `active_branch_id: null`
- set `next_action: run novelty-check on the candidate set and select one primary idea`
- set `decision_mode: auto-report`
- set `human_attention: none`
- clear `decision_type` and `decision_options_ref`
- set `last_completed_skill: idea-creator`
- refresh `last_updated`

## Failure Handling

Stop without writing if:

- no usable literature-review artifact exists
- the candidate set would be vague, non-falsifiable, or obviously outside project constraints
- the only way to continue would be to fabricate evidence or ignore known failure patterns

When stopping, report the exact gap.

## Self-Check

- [ ] Produced a bounded candidate set rather than an ungoverned idea swarm
- [ ] Wrote only the candidate artifact plus steering updates in `STATE.md`
- [ ] Kept the active experiment line inactive
- [ ] Preserved traceability back to the literature-review artifact
- [ ] Left `experiment-memory.md`, `decision-tree.md`, and evidence ledgers untouched
