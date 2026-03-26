# `novelty-check.md` Bootstrap Contract

## Purpose

`projects/<slug>/workspace/bootstrap/novelty-check.md` is the bootstrap decision artifact that screens candidate ideas conservatively and selects the primary idea for planning.

It exists so `experiment-plan` can consume a traceable idea-selection result rather than a vague conversational memory.

## Canonical Location

Recommended path:

- `projects/<slug>/workspace/bootstrap/novelty-check.md`

## Relationship to Canonical State

This file is a bootstrap review artifact.

It may justify later steering updates such as:

- `STATE.md.active_idea_id`
- `STATE.md.next_action`

But it is not itself canonical Project State.

## Suggested Structure

```md
# Novelty Check

## Identity
- project_id:
- generated_at:
- source_review_ref:
- source_candidates_ref:

## Screening Table
| idea_id | overlap_risk | novelty_strength | empirical_tractability | integrity_risk | decision | notes |
|---------|--------------|------------------|------------------------|----------------|----------|-------|

## Selected Idea
- selected_idea_id:
- selection_rationale:
- why_now:
- main_failure_watchouts:

## Optional Cross-Model Review
- reviewer:
- summary:
- adopted_points:
- residual_disagreements:

## Deferred Ideas
| idea_id | defer_reason | revisit_trigger |
|---------|--------------|-----------------|
```

## Rules

1. Select exactly one primary idea when autonomous continuation is possible.
2. Preserve deferred ideas explicitly instead of letting them disappear.
3. Explain overlap risk and integrity risk directly.
4. The selected idea may later become `STATE.md.active_idea_id`, but this artifact itself is still non-canonical.
5. `Optional Cross-Model Review` is advisory only and must not silently override the selected idea.
