# Field Conventions

This document defines the shared naming and reference conventions for Link-Research.

## Naming Categories

### Identity Fields

Use `*_id` for stable logical identities.

Examples:

- `project_id`
- `idea_id`
- `experiment_id`
- `branch_id`
- `run_id`
- `failure_id`
- `paper_id`

Rules:

- IDs identify logical objects, not files.
- IDs should stay stable even if file paths change.
- IDs should be short, human-readable, and repository-safe.

### File Location Fields

Use `*_path` for explicit file locations.

Examples:

- `anchor_path`
- `archive_path`
- `config_path`

Rules:

- Paths point to repository files or generated workspace files.
- Paths should be stored as repository-relative paths unless a runtime layer explicitly requires absolute paths.
- Paths should not be used as a replacement for logical IDs.

### Content Reference Fields

Use `*_ref` for references to specific records, sections, or evidence anchors.

Examples:

- `latest_result_ref`
- `latest_analysis_ref`
- `evidence_ref`
- `archive_ref`
- `source_ref`

Rules:

- Refs may point into tables, sections, archive records, or ledger entries.
- Refs should be stable enough for Codex and lint tooling to resolve.
- Refs are allowed to include file plus selector syntax such as `results.tsv#exp-003-run-02`.

## Timestamp Convention

Use ISO 8601 timestamps with timezone offset.

Example:

- `2026-03-24T19:10:00+08:00`

Rules:

- Use `*_at` suffix for JSON-style state files when practical.
- Use `last_updated` when representing a human-facing summary field.

## Boolean Convention

Use explicit boolean intent names.

Preferred:

- `needs_human_decision`
- `archive_recommended`
- `resume_safe`

Avoid vague boolean names such as:

- `active`
- `ready`
- `valid`

unless the object schema defines the scope precisely.

## Enum Convention

Use lowercase kebab-case or lowercase snake-case consistently inside one file format.

Repository recommendation:

- Markdown-facing state summaries: lowercase tokens as values
- JSON state files: lowercase kebab-case

Examples:

- `phase1`
- `phase2`
- `waiting-human`
- `auto-report`
- `near-miss`

## Cross-File Reference Rule

Every important verdict or steering decision should be traceable through these layers:

1. logical object ID
2. file path when relevant
3. evidence reference when relevant

Example chain:

- `experiment_id: exp-003`
- `anchor_path: projects/leo-fl-agg/plans/idea-003/anchor.md`
- `latest_result_ref: results.tsv#exp-003-run-02`

## Ownership Rule

Each file view should have one primary owner object.

Examples:

- `STATE.md` -> Project State
- `experiment-memory.md` -> Experiment State
- `review-state.json` -> Run State
- `lessons-learned.md` -> Memory State

## Human Attention Convention

Use two fields together when a system may need operator attention:

- `decision_mode`
- `human_attention`

Recommended values:

- `decision_mode: auto | auto-report | human-gated`
- `human_attention: none | async-review | required-now`

## Future Lint Targets

These conventions should later be enforced by harness lint:

- required IDs present where expected
- no path fields used where IDs should be used
- no verdict state without evidence refs
- no duplicate object ownership across primary view files

