---
name: analyze-results
description: Use after a new result group has been recorded to write a structured analysis artifact before drift and judge consume the evidence.
---

# Analyze Results

## Overview

Interpret the latest result group conservatively into a structured analysis artifact.

`analyze-results` owns `analysis-report.json`. It does not own verdicts, drift decisions, or the raw evidence ledger.

## When to Use

Use when:

- a new `latest_result_ref` exists for the active line
- the corresponding result group has no current analysis artifact
- the project is ready to interpret evidence before drift review

Do not use when:

- no result group is available
- the evidence is too incomplete to support a responsible analysis

## Read / Write Contract

### Read

- `projects/<slug>/project-brief.md`
- `projects/<slug>/STATE.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/plans/<idea>/anchor.md`
- `projects/<slug>/results.tsv`
- `projects/<slug>/workspace/results/<result-group-id>/config-snapshot.json` through `latest_result_ref`
- attributable files under `projects/<slug>/workspace/results/<result-group-id>/...`
- `docs/views/analysis-report-view.md`

### Write

- `projects/<slug>/workspace/results/<result-group-id>/analysis-report.json`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/STATE.md`

### Must Not Write

- `projects/<slug>/results.tsv`
- `projects/<slug>/plans/<idea>/anchor.md`
- `projects/<slug>/review-state.json`
- `projects/<slug>/decision-tree.md`
- `memory/*`
- `projects/<slug>/workspace/dashboard-data.json`

## Required Input Checks

Before proceeding, verify:

- `latest_result_ref` is non-null and resolvable
- the referenced result group has at least one valid result row
- `config-snapshot.json` exists for that result group
- the active anchor is readable

If the evidence bundle is incomplete, stop and report the exact missing piece instead of improvising analysis.

## Protocol

### 1. Resolve The Latest Result Group

Use `experiment-memory.md` plus `results.tsv` to identify the latest active `result_group_id`.

Resolve:

- the result rows
- the result-group artifact directory
- `config-snapshot.json`
- any attributable run files needed to interpret the evidence

### 2. Interpret Against The Active Anchor

Read the bound `anchor.md` so the analysis stays aligned with:

- the locked claim
- the primary success criteria
- the required baselines
- the red lines and disconfirming signals

### 3. Write The Structured Analysis Artifact

Write `projects/<slug>/workspace/results/<result-group-id>/analysis-report.json` using the documented evidence contract.

The artifact should include:

- concise summary
- primary findings
- metric interpretation
- evidence gaps
- anomalies
- recommended next action
- refs back to the result group and artifact bundle

Keep the interpretation conservative. Do not issue a verdict here.

### 4. Update Experiment State

Update `experiment-memory.md`:

- set `status: analyzed`
- set `latest_analysis_ref` to the new analysis artifact
- refresh the latest evidence summary and latest analysis block
- keep drift and judge fields unresolved until their skills run
- set `next_experiment_action: wait-human`
- refresh `last_updated`

### 5. Update Project Steering State

Update `STATE.md`:

- keep `phase: phase1`
- set `project_status: running`
- set `next_action: run drift-detector on the latest analysis artifact`
- set `decision_mode: auto-report`
- set `human_attention: none`
- clear `decision_type` and `decision_options_ref`
- set `last_completed_skill: analyze-results`
- refresh `last_updated`

## Failure Handling

Stop without writing if:

- the latest result group cannot be resolved
- required evidence rows are missing
- `config-snapshot.json` is missing
- the active anchor is unreadable

When stopping, report the exact missing ref or artifact.

## Self-Check

- [ ] Wrote only `analysis-report.json` plus canonical state updates in `experiment-memory.md` and `STATE.md`
- [ ] Did not mutate `results.tsv`
- [ ] Kept interpretation aligned to the locked anchor
- [ ] Left drift and judge decisions to their own skills
- [ ] Preserved clear refs back to the latest result group
