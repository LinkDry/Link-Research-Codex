# `literature-review.md` Bootstrap Contract

## Purpose

`projects/<slug>/workspace/bootstrap/literature-review.md` is the durable bootstrap artifact for the initial landscape scan.

It exists to capture the scoped literature context that later bootstrap skills consume without pretending this file is canonical Project State or Experiment State.

## Canonical Location

Recommended path:

- `projects/<slug>/workspace/bootstrap/literature-review.md`

## Relationship to Canonical State

This file is a bootstrap planning artifact, not a primary view.

It may inform:

- `idea-creator`
- `novelty-check`
- `experiment-plan`

But canonical active state still lives in:

- `projects/<slug>/STATE.md`
- `projects/<slug>/experiment-memory.md`

## Suggested Structure

```md
# Literature Review

## Identity
- project_id:
- generated_at:
- intake_mode:

## Search Scope
- research_domain:
- target_problem:
- search_queries:
- seed_papers:

## Reviewed Sources
| source_id | title | year | relevance | novelty_signal | warning_flags |
|-----------|-------|------|-----------|----------------|---------------|

## Opportunity Map
| opportunity_id | summary | evidence_basis | why_open | failure_signals | recommended_follow_up |
|----------------|---------|----------------|----------|-----------------|-----------------------|

## Reusable Warnings
- memory_refs:
- failure_refs:
- notes:
```

## Rules

1. Keep the artifact scoped to the current project intake.
2. Record uncertainty explicitly instead of overclaiming novelty.
3. Reuse global lessons and failure patterns by reference rather than copying them wholesale.
4. Do not treat this file as the canonical owner of the active idea or active branch.
