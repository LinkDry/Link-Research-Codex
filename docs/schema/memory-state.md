# Memory State Schema

## Purpose

Memory State stores cross-project long-term learning.

It answers:

- what lessons were learned
- what patterns recur across projects
- what capability gaps remain unresolved
- what failure classes should warn future ideas

## Non-Goals

Memory State does not store:

- current project steering context
- raw experiment results
- long-running orchestration progress
- project-local archive details as the primary source

## Primary File Views

- `memory/lessons-learned.md`
- `memory/failure-library.md`
- `memory/archive/`

## Subdomains

### Lessons

Reusable observations extracted from project events.

Recommended fields:

- `lesson_id`
- `date`
- `scope`
- `project_id`
- `idea_id`
- `branch_id`
- `source_type`
- `source_ref`
- `category`
- `polarity`
- `summary`
- `evidence_ref`
- `reusable`
- `similarity_tags`

### Patterns

Promoted recurring lessons.

Recommended fields:

- `pattern_id`
- `pattern_type`
- `first_seen`
- `last_seen`
- `occurrence_count`
- `summary`
- `trigger_signals`
- `recommended_action`
- `source_lesson_refs`
- `confidence`

### Capability Gaps

Long-lived system weaknesses or missing capabilities.

Recommended fields:

- `gap_id`
- `date`
- `gap_type`
- `description`
- `impact_level`
- `detected_in`
- `workaround`
- `proposed_fix`
- `status`

### Failure Library

Structured failure cases used to warn future idea generation and validation.

Recommended fields:

- `failure_id`
- `project_id`
- `idea_id`
- `branch_id`
- `failure_class`
- `summary`
- `why_it_failed`
- `when_to_warn_again`
- `similarity_tags`
- `hard_red_flags`
- `soft_red_flags`
- `archive_ref`
- `evidence_refs`

## Global vs Project-Local Rule

- Project-local archive files contain full case detail.
- Global memory stores reusable abstractions and references.
- Global compacted lesson history belongs in `memory/archive/`, not project archives.

## Promotion Rule

The intended learning flow is:

1. failure or success event occurs
2. project archive captures full detail
3. lessons capture reusable summary
4. recurring lessons promote to patterns or failure classes
5. future idea generation checks those patterns before deep investment

## View Design Rule

`memory/lessons-learned.md` should stay human-readable and structured.

It should present:

- recent lessons
- persistent patterns
- capability gap log
- meta-patterns

It should reference project-local archives instead of duplicating their full detail.
