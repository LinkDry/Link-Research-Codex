# `experiment-plan.md` Input Contract

## Purpose

`projects/<slug>/plans/<idea>/experiment-plan.md` is the structured planning input consumed by `anchor-wrapper`.

Its job is to define the exact experimental intent before an anchor is locked.

It must be specific enough that `anchor-wrapper` can:

- extract a falsifiable claim
- lock measurable success criteria
- distinguish mutable from immutable variables
- record red lines and falsifiers

## Owner Relationship

`experiment-plan.md` is a planning input, not a canonical state owner.

It exists to feed `anchor-wrapper`, future execution skills, and archive records.

Canonical active state still lives in:

- `STATE.md`
- `experiment-memory.md`
- `review-state.json`

## Canonical Path

Use this path for the active branch plan:

- `projects/<slug>/plans/<idea>/experiment-plan.md`

If future variants are needed, keep this file as the currently active plan and archive older versions explicitly rather than relying on wildcard discovery.

## Required Sections

```md
# Experiment Plan

## Identity
- project_id:
- idea_id:
- branch_id:
- experiment_id:
- authoring_skill:
- planned_at:

## Experiment Intent
- hypothesis_statement:
- why_it_might_work:
- novelty_basis:

## Success Criteria
- primary_metric:
- comparator:
- target_value:
- evaluation_split:
- minimum_effect_size:
- required_baselines:

## Experimental Design
- method_under_test:
- baseline_methods:
- datasets:
- evaluation_protocol:

## Variable Boundaries
- mutable_variables:
- immutable_variables:

## Stopping Rules
- red_lines:
- disconfirming_signals:
- archive_if_true:

## Evidence Plan
- source_refs:
- expected_artifacts:
- expected_results_rows:
- analysis_requirements:

## Open Risks
- methodological_risks:
- implementation_risks:
- integrity_risks:

## Optional Advisory Review
- reviewer:
- summary:
- adopted_changes:
- unresolved_disagreements:
```

## Field Rules

### `hypothesis_statement`

- must be falsifiable
- must describe the specific claim under test
- must not be a vague aspiration such as "improve performance"

### `primary_metric`, `comparator`, `target_value`, `evaluation_split`

- together these fields must define metric, comparator, threshold, and evaluation target
- examples:
  - `primary_metric: macro_f1`
  - `comparator: >=`
  - `target_value: 0.78`
  - `evaluation_split: dev`

### `minimum_effect_size`

- defines the smallest effect that still counts as meaningful
- may be qualitative only if paired with a quantitative primary criterion

### `mutable_variables`

- list only variables that may change during TWEAK iterations without invalidating the idea
- each item should include an initial value or planned range

### `immutable_variables`

- list variables that define the idea itself
- changing these requires a new branch or anchor version

### `red_lines`

- minimum of two
- each red line should be evidence-checkable

### `source_refs`

- cite the papers, notes, or observations motivating the plan
- use repository-relative refs or stable identifiers when possible

### `disconfirming_signals`

- list the concrete observations that would count against the hypothesis even if no formal red line is crossed
- use this field to make later rethink/archive decisions auditable rather than ad hoc

## Validation Rule

`anchor-wrapper` must refuse to lock an anchor if any of the following are missing:

- falsifiable hypothesis
- quantitative success criteria fields
- at least one mutable or immutable variable
- at least two red lines

## Content That Does Not Belong Here

- live run-step progress
- finalized judge verdicts
- drift scores
- retrospective lessons learned

## Relationship to `anchor.md`

- `experiment-plan.md` is editable while planning remains open.
- `anchor.md` is the locked record created from this plan.
- Once the anchor is created, later scientific pivots should create a new plan revision or branch rather than silently rewriting the locked anchor.

## Advisory Review Rule

Any optional external or cross-model critique captured in this file is advisory only.

The plan owner may use it to strengthen the experiment design before anchor lock, but it must not silently rewrite the meaning of a later locked anchor.
