---
name: literature-review
description: Use at the start of Phase 1 bootstrap to turn the project brief into a scoped literature landscape scan without prematurely inventing canonical experiment state.
---

# Literature Review

## Overview

Build the first durable research-context artifact for a project.

`literature-review` is a bootstrap planning skill. It does not create an active experiment line. It produces a scoped landscape artifact that later bootstrap skills can consume safely.

## When to Use

Use when:

- `project-brief.md` contains a usable `intake_mode`
- the project is entering or already in Phase 1 bootstrap
- there is no trustworthy current literature-review artifact for the present intake

Do not use when:

- the project already has an active anchored line and no bootstrap reset was requested
- the intake configuration is too incomplete to define a search scope

## Read / Write Contract

### Read

- `projects/<slug>/project-brief.md`
- `projects/<slug>/STATE.md`
- `memory/lessons-learned.md`
- `memory/failure-library.md`
- `docs/views/literature-review-view.md`

### Write

- `projects/<slug>/workspace/bootstrap/literature-review.md`
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

- `project-brief.md` exists and is structurally readable
- `intake_mode` is either `direction-search` or `seed-papers`
- `target_problem` is non-empty
- at least one of these is present:
  - a usable `direction_prompt`
  - one or more `seed_papers`

If the intake is incomplete, stop and report the exact missing field instead of fabricating a search brief.

## Protocol

### 1. Load Intake Context

Read:

- `project-brief.md` for research goal, intake mode, constraints, venue targets, execution resources, and integrity red lines
- `STATE.md` for the current project phase and bootstrap posture
- relevant recurring patterns from `memory/lessons-learned.md` and `memory/failure-library.md`

### 2. Choose The Review Mode

If `intake_mode: direction-search`:

- expand from the target problem into problem families, baseline clusters, evaluation norms, and likely dead ends

If `intake_mode: seed-papers`:

- center the review on the supplied seed papers
- map nearest-neighbor work, claimed differentiators, reused evaluation setups, and likely novelty traps

### 3. Build A Conservative Opportunity Map

Write `projects/<slug>/workspace/bootstrap/literature-review.md` using the documented bootstrap contract.

The artifact should capture:

- the scoped search frame
- the most relevant papers or artifacts reviewed
- candidate opportunity zones worth ideation
- repeated failure signals or anti-patterns drawn from global memory
- unresolved questions that still need idea-level narrowing

Keep the artifact evidence-oriented. Do not claim a definitive novelty gap unless the evidence supports it.

### 4. Update Project Steering State

Update `STATE.md` conservatively:

- set `phase: phase1` if the project was still in `phase0`
- set `project_status: running`
- keep `active_idea_id: null`
- keep `active_branch_id: null`
- set `next_action: generate bounded candidate ideas from the literature review artifact`
- set `decision_mode: auto-report`
- set `human_attention: none`
- clear `decision_type` and `decision_options_ref`
- refresh `risk_level` and `blockers` only if the review surfaced a real constraint
- set `last_completed_skill: literature-review`
- refresh `last_updated`

## Failure Handling

Stop without writing if:

- the intake mode is unreadable or unsupported
- the project brief does not provide enough direction to scope a review
- the requested review would require inventing sources or hidden state

When stopping, report the exact missing field or contract gap.

## Self-Check

- [ ] Wrote only the bootstrap literature artifact plus steering updates in `STATE.md`
- [ ] Did not create an active experiment line
- [ ] Reused lessons and failure patterns by reference rather than copying global memory into canonical project state
- [ ] Kept novelty claims conservative and traceable
- [ ] Left `experiment-memory.md`, `results.tsv`, and `review-state.json` untouched
