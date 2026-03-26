---
name: anchor-wrapper
description: Use when an experiment plan is complete and a branch needs its first immutable anchor before any validation run, drift check, or judge verdict.
---

# Anchor Wrapper

## Overview

Lock a write-once anchor from `projects/<slug>/plans/<idea>/experiment-plan.md`.

The anchor is the scientific contract for the active experiment line. After it is created, the current branch must test that contract rather than quietly redefining it.

## When to Use

Use when:

- `project-brief.md` is filled enough to define scope and constraints
- `STATE.md` and `experiment-memory.md` identify the active idea and branch
- `projects/<slug>/plans/<idea>/experiment-plan.md` exists and is complete
- the branch is ready to move from planning into validation

Do not use when:

- an anchor already exists for the active branch
- the plan is still missing quantitative success criteria
- the hypothesis has materially changed and needs a new branch or human-approved anchor revision

## Read / Write Contract

### Read

- `projects/<slug>/project-brief.md`
- `projects/<slug>/STATE.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/plans/<idea>/experiment-plan.md`

### Write

- `projects/<slug>/plans/<idea>/anchor.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/STATE.md`

### Must Not Write

- `projects/<slug>/results.tsv`
- `projects/<slug>/review-state.json`
- `projects/<slug>/workspace/dashboard-data.json`
- any `_index.md` projection

## Required Input Checks

Before locking the anchor, verify the experiment plan includes:

- a falsifiable `hypothesis_statement`
- a concrete `why_it_might_work`
- measurable success criteria through `primary_metric`, `comparator`, `target_value`, and `evaluation_split`
- at least one `mutable_variables` or `immutable_variables` entry
- at least two `red_lines`
- explicit `source_refs` and `disconfirming_signals`

If any of these are missing, stop and report the gap. Do not write a partial anchor.

## Protocol

### 1. Load Active Context

Read:

- `STATE.md` for `project_id`, `phase`, `active_idea_id`, and `active_branch_id`
- `experiment-memory.md` for `experiment_id`, current `status`, existing `anchor_path`, and `anchor_version`
- `project-brief.md` for project constraints and red lines that may narrow claim scope

Stop if:

- no active idea or branch is selected
- no active experiment line exists
- an anchor is already bound for this branch or an `anchor.md` already exists for it

### 2. Load Experiment Plan

Read `projects/<slug>/plans/<idea>/experiment-plan.md`.

Stop if the file is missing or incomplete.

Treat the plan as the only planning input. Do not scan wildcard files or infer extra state from projections.

### 3. Validate Anchor Readiness

Confirm:

- the `hypothesis_statement` is falsifiable rather than aspirational
- the success criteria fields include metric, comparator, threshold, and evaluation target
- mutable and immutable boundaries are distinguishable
- red lines are concrete and evidence-checkable
- `source_refs` and `disconfirming_signals` are present
- required baselines do not conflict with project constraints in `project-brief.md`

If the plan fails validation:

- stop without writing any file
- tell the operator exactly what must be fixed in `experiment-plan.md`

### 4. Write `anchor.md`

Write `projects/<slug>/plans/<idea>/anchor.md` as a write-once artifact using this shape:

```md
# Anchor Record

## Identity
- project_id:
- idea_id:
- branch_id:
- experiment_id:
- anchor_version: v1
- locked_at:

## Hypothesis
- claim:
- why_it_might_work:
- novelty_basis:

## Success Criteria
- primary_success_criteria:
- minimum_effect_size:
- required_baselines:

## Evidence Boundaries
- allowed_mutations:
- locked_invariants:
- red_lines:
- source_refs:

## Falsifiers
- disconfirming_signals:
- archive_if_true:

## Operator Notes
- notes:
```

Rules:

- initial anchors use `anchor_version: v1`
- map `hypothesis_statement` into `claim`
- map the success criteria fields into `primary_success_criteria`
- map `mutable_variables` into `allowed_mutations`
- map `mutable_variables` into `allowed_mutations`
- map `immutable_variables` into `locked_invariants`
- carry `red_lines`, `source_refs`, `disconfirming_signals`, and `archive_if_true` through without inventing replacements
- preserve plan wording where precision matters
- do not add new schema fields ad hoc
- if a replacement anchor is later needed, create a new versioned anchor or new branch rather than rewriting this file

### 5. Bind the Anchor to Experiment State

Update `experiment-memory.md`:

- `status` -> `anchored`
- `anchor_path` -> `projects/<slug>/plans/<idea>/anchor.md`
- `anchor_version` -> `v1`
- `next_experiment_action` -> `run-first-experiment`
- `last_updated` -> current timestamp

Update the `Anchor Summary` section:

- `locked_anchor_path`
- `anchor_claim_summary`
- `anchor_constraints`

Keep the summary short and traceable to the locked anchor.

### 6. Update Project Steering State

Update `STATE.md`:

- `phase` -> `phase1` if still `phase0`
- `project_status` -> `running`
- `active_idea_id`
- `active_branch_id`
- `next_action` -> run the first experiment against the locked anchor
- `last_completed_skill` -> `anchor-wrapper`
- `last_updated` -> current timestamp

Do not invent new steering fields.

## Failure Handling

Stop without writing if:

- `experiment-plan.md` does not exist
- the plan lacks quantitative success criteria
- the hypothesis is not falsifiable
- red lines are missing or fewer than two
- `source_refs` or `disconfirming_signals` are missing
- an anchor already exists for the branch

When stopping, report the missing section or policy violation explicitly so the plan can be repaired.

## Self-Check

- [ ] Read the canonical `experiment-plan.md` path, not a wildcard file set
- [ ] Wrote only `anchor.md`, `experiment-memory.md`, and `STATE.md`
- [ ] Did not touch `results.tsv`, `review-state.json`, dashboard data, or any `_index.md`
- [ ] Bound `anchor_path` and `anchor_version` through canonical Experiment State fields only
- [ ] Refused to create an anchor if the plan was incomplete
- [ ] Refused to rewrite an existing anchor in place
