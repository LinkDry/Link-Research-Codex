---
name: novelty-check
description: Use during Phase 1 bootstrap to conservatively screen candidate ideas, select one primary idea, and prepare the project for experiment-plan authoring.
---

# Novelty Check

## Overview

Filter the candidate set before committing the project to a concrete plan.

`novelty-check` does not create the active experiment line. It writes a bootstrap decision artifact and, when one candidate is clearly preferred, may set `STATE.md.active_idea_id` to that selected idea.

## When to Use

Use when:

- `idea-candidates.md` exists
- the project needs one primary candidate for planning

Do not use when:

- the candidate set is missing
- the project already has a current active line and no bootstrap reset was requested

## Read / Write Contract

### Read

- `projects/<slug>/project-brief.md`
- `projects/<slug>/STATE.md`
- `projects/<slug>/workspace/bootstrap/literature-review.md`
- `projects/<slug>/workspace/bootstrap/idea-candidates.md`
- `memory/lessons-learned.md`
- `memory/failure-library.md`
- `docs/views/novelty-check-view.md`

### Write

- `projects/<slug>/workspace/bootstrap/novelty-check.md`
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

- `idea-candidates.md` exists and is structurally readable
- candidate ideas carry stable `idea_id` values
- project constraints and integrity red lines are readable

If the candidate set is too weak or ambiguous to screen responsibly, stop and report that gap.

## Protocol

### 1. Load Screening Inputs

Read:

- the project brief
- the literature-review artifact
- the idea-candidate artifact
- relevant lessons or failure patterns that materially affect novelty or validation risk

### 2. Screen Each Candidate Conservatively

For each candidate, assess:

- overlap risk with the reviewed literature
- novelty strength
- empirical tractability
- integrity or overclaim risk
- whether it still fits the project constraints

### 3. Optional Cross-Model Review

If Codex review is available through local Codex execution, you may request an advisory second opinion on:

- novelty overclaim risk
- whether the top-ranked idea is genuinely the strongest next line
- hidden validation blockers that would make the idea fragile in Phase 1
- whether a conservative single-winner selection is justified from the current evidence

Rules:

- treat the external review as advisory only
- do not let it select the winner on its own
- if disagreement is material, keep the more conservative screening rationale
- if no responsible single selection remains after conservative review, stop and report the ambiguity instead of forcing a winner

Record any adopted critique in `novelty-check.md`.

### 4. Select Exactly One Primary Idea

Choose one primary idea when autonomous continuation is possible.

If multiple ideas remain plausible:

- preserve runners-up in the artifact
- explain why the selected idea is the current best next move

Do not silently drop the alternatives.

### 5. Write The Novelty Decision Artifact

Write `projects/<slug>/workspace/bootstrap/novelty-check.md` using the documented bootstrap contract.

The artifact must include:

- a screening table for the candidate set
- one `selected_idea_id`
- rationale for the selection
- failure watchouts
- deferred ideas plus revisit triggers

### 6. Update Project Steering State

Update `STATE.md`:

- keep `phase: phase1`
- keep `project_status: running`
- set `active_idea_id` to the selected idea
- keep `active_branch_id: null`
- set `next_action: create the experiment plan for the selected idea`
- set `decision_mode: auto-report`
- set `human_attention: none`
- clear `decision_type` and `decision_options_ref`
- set `last_completed_skill: novelty-check`
- refresh `last_updated`

## Failure Handling

Stop without writing if:

- the candidate artifact is missing or unreadable
- idea IDs are absent or ambiguous
- the selected idea cannot be justified without overstating novelty
- conservative screening plus external critique leaves no clearly defensible single primary idea

When stopping, report the exact ambiguity or missing input.

## Self-Check

- [ ] Selected exactly one primary idea for the next planning step
- [ ] Preserved deferred ideas explicitly
- [ ] Updated only the novelty-check artifact plus `STATE.md`
- [ ] Did not create an experiment line or anchor
- [ ] Kept novelty claims conservative and evidence-backed
- [ ] Treated any cross-model review as advisory only
