# Experiment State Schema

## Purpose

Experiment State describes the validation lifecycle for one `idea x branch` line.

It answers:

- what is currently being validated
- which anchor is bound
- how many iterations have run
- what the latest evidence says
- what drift and judge currently think
- what should happen next

## Non-Goals

Experiment State does not store:

- project-wide steering state
- long-running orchestration progress
- cross-project lessons
- full raw result payloads

## Primary File Views

- `projects/<slug>/experiment-memory.md` - human-facing experiment view
- `projects/<slug>/results.tsv` - raw evidence ledger
- `projects/<slug>/plans/<idea>/anchor.md` - immutable hypothesis evidence
- `projects/<slug>/decision-tree.md` - branch comparison context

## Current Branch Slot Rule

Experiment State is branch-aware, but the canonical `experiment-plan.md` and `anchor.md` paths are
still idea-scoped today.

Until branch-scoped paths are introduced, those files should be treated as a single active branch
slot per `idea_id`.

That means same-idea sibling branch activation must move through an explicit governance decision
unless the existing slot is being safely repurposed after the prior line is closed or superseded.

## Required Fields

| Field | Type | Description | Primary Consumer |
|------|------|-------------|------------------|
| `experiment_id` | id/null | stable active experiment-line identity, or `null` when no line is selected | all layers |
| `idea_id` | id/null | owning idea for the active line, or `null` when no line is selected | Codex |
| `branch_id` | id/null | current branch identity, or `null` when no line is selected | Codex |
| `status` | enum | lifecycle state for this experiment line | Codex, dashboard |
| `anchor_path` | path/null | bound anchor file | Codex, audit |
| `anchor_version` | string/null | anchor version or variant label | Codex |
| `iteration_count` | integer | completed iteration count | Codex, judge |
| `latest_result_ref` | ref/null | latest results ledger reference | Codex, dashboard |
| `latest_analysis_ref` | ref/null | latest structured analysis artifact reference | Codex |
| `latest_drift_score` | number/null | latest drift score | Codex, dashboard |
| `latest_drift_decision` | enum/null | latest drift decision | Codex |
| `latest_judge_verdict` | enum/null | latest judge verdict | Codex |
| `success_criteria_status` | enum | current success state | Codex |
| `human_review_required` | boolean | whether human review is required | operator |
| `archive_recommended` | boolean | whether archive is recommended | Codex |
| `next_experiment_action` | enum | next recommended experiment action | Codex |
| `last_updated` | timestamp | latest refresh time | all views |

## Optional Fields

| Field | Type | Description |
|------|------|-------------|
| `parent_branch_id` | id/null | parent branch when forked |
| `judge_confidence` | enum/null | confidence attached to latest judge verdict |
| `latest_judge_report_ref` | ref/null | pointer to the structured judge rationale artifact |
| `notes_ref` | ref/null | pointer to extra diagnostic notes |

## Enums

### `status`

- `planned`
- `anchored`
- `running`
- `analyzed`
- `drifted`
- `judged`
- `archived`
- `invalidated`

### `latest_drift_decision`

- `consistent`
- `drift-detected`
- `anchor-violation`
- `red-line`

### `latest_judge_verdict`

- `pass`
- `tweak`
- `rethink`
- `archive`

### `judge_confidence`

- `low`
- `medium`
- `high`

### `success_criteria_status`

- `met`
- `near-miss`
- `unmet`
- `invalidated`
- `unknown`

### `next_experiment_action`

- `run-first-experiment`
- `rerun`
- `tweak-mutable-vars`
- `judge-ready`
- `branch`
- `archive`
- `phase2-ready`
- `wait-human`

## Phase 2 Handoff Rule

`phase2-ready` means the active experiment line has cleared the Phase 1 validation gate and is ready to hand off into Phase 2.

It does not, by itself, mean the project has already entered `phase2`.

`phase2-ready` may coexist with a human-gated `phase2-handoff` decision in `STATE.md` when the experiment has passed but the publication path still requires an explicit operator choice.

While that `phase2-handoff` decision is still pending, publication skills must not take ownership of
Phase 2 yet.

The actual `STATE.md.phase` transition happens only when the Phase 2 orchestrator or publishing workflow starts.

## Forced-Stop Rule

After 3 consecutive non-pass verdicts on the same branch, `next_experiment_action` must not remain a same-line tweak or rerun posture.

At that point the next action must move to one of:

- `branch`
- `archive`
- `wait-human`

## Evidence Rule

No meaningful verdict should exist without a traceable evidence path:

- `anchor_path`
- `latest_result_ref`
- `latest_analysis_ref`

For judged lines, `latest_judge_report_ref` should point to the structured verdict artifact that explains why the verdict was chosen.

## View Design Rule

`experiment-memory.md` should combine:

- one current snapshot block
- structured history tables
- latest analysis detail block
- completed experiment-line summary table

It should not become the only storage location for raw experiment results.
