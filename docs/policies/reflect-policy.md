# Reflect Policy

## Purpose

This document is the single authoritative policy for `reflect`.

`reflect` is a session-synthesis skill, not a catch-all maintenance skill. Its job is to convert session outcomes into reusable memory while keeping the compact project summary current.

## Allowed Writes

### `memory/lessons-learned.md`

`reflect` may update only these sections:

- `Recent Lessons`
- `Capability Gaps`
- `Promotion Queue`

It may:

- append new reusable lessons
- update or close capability-gap rows
- queue repeated lessons or gaps for later promotion

It must not:

- write `memory/failure-library.md`
- invent low-signal filler lessons just to satisfy a checklist

### `projects/<slug>/STATE.md`

`reflect` may refresh only compact summary fields:

- `next_action`
- `blockers`
- `risk_level`
- `last_completed_skill`
- `last_updated`

It should treat these as summary fields derived from current canonical state rather than as new scientific decisions.

## Forbidden Writes

`reflect` must not write:

- `projects/<slug>/review-state.json`
- `projects/<slug>/project-brief.md`
- `projects/<slug>/results.tsv`
- any anchor, judge, or archive artifact
- `memory/failure-library.md`
- dashboard projections

## Session Summary Rule

The session summary produced by `reflect` is primarily user-facing output.

If an orchestration run needs a machine-readable summary, the run owner should persist it in `review-state.json`; `reflect` does not own that file.

## Capability Gap Rule

Capability gaps discovered during the session should be normalized into the `Capability Gaps` table in `memory/lessons-learned.md`.

Allowed gap types:

- `tool-gap`
- `doc-gap`
- `constraint-gap`
- `data-gap`
- `skill-gap`

## Promotion Queue Rule

If the same warning signal or lesson pattern recurs, `reflect` should add a queue item to `Promotion Queue` rather than directly modifying broader governance docs or the failure library.

This keeps pattern promotion explicit and reviewable.

## Housekeeping Boundary

`reflect` does not trigger any hidden maintenance flow.

If housekeeping is needed, report it in the output or leave it for the orchestrator.
