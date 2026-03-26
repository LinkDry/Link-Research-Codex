# `idea-candidates.md` Bootstrap Contract

## Purpose

`projects/<slug>/workspace/bootstrap/idea-candidates.md` is the durable bootstrap artifact for the bounded candidate-idea set derived from the literature review.

It exists to keep ideation traceable before a single active experiment line is canonically created.

## Canonical Location

Recommended path:

- `projects/<slug>/workspace/bootstrap/idea-candidates.md`

## Relationship to Canonical State

This file is a bootstrap planning artifact.

It may inform:

- `novelty-check`
- `experiment-plan`

It does not replace canonical active state in:

- `projects/<slug>/STATE.md`
- `projects/<slug>/experiment-memory.md`

## Suggested Structure

```md
# Idea Candidates

## Identity
- project_id:
- generated_at:
- source_review_ref:

## Candidate Table
| idea_id | title | claim_summary | novelty_basis | validation_shape | key_risks | source_refs | recommended |
|---------|-------|---------------|---------------|------------------|-----------|-------------|-------------|

## Branch Seeds
| idea_id | possible_branch_seed | why_it_deserves_separate_validation |
|---------|----------------------|------------------------------------|

## Notes
- why_these_candidates:
- deferred_candidates:
```

## Rules

1. Keep the candidate set bounded, normally 2-5 ideas.
2. Every candidate should already be falsifiable enough to support later planning.
3. Candidate IDs should be stable and repository-safe, such as `idea-001`.
4. This file should not silently activate an experiment line by itself.
