# `judge-report.json` Evidence Contract

## Purpose

`judge-report.json` is the structured verdict artifact for one judged experiment iteration.

It exists so `judge`, `overnight`, `archive`, and future lint tooling can consume detailed verdict rationale without treating Markdown prose as hidden state.

## Canonical Location

Recommended path:

- `projects/<slug>/workspace/reviews/<experiment_id>/judge-report-<iteration>.json`

`latest_judge_report_ref` in Experiment State should normally point to this artifact.

## Relationship to Canonical State

`judge-report.json` is a secondary evidence artifact owned by Experiment State.

It does not replace:

- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/STATE.md`
- `projects/<slug>/decision-tree.md`

Instead:

- `experiment-memory.md` stores the compact active verdict snapshot
- `STATE.md` stores current steering posture
- `decision-tree.md` stores branch-governance summary
- `judge-report.json` stores detailed rationale and decision options

## Required JSON Shape

```json
{
  "judge_report_id": "judge-exp-001-iter-03",
  "project_id": "proj-001",
  "experiment_id": "exp-001",
  "idea_id": "idea-001",
  "branch_id": "branch-main",
  "iteration": 3,
  "generated_at": "2026-03-24T23:40:00+08:00",
  "anchor_path": "projects/demo/plans/idea-001/anchor.md",
  "latest_result_ref": "results.tsv#rg-003",
  "latest_analysis_ref": "projects/demo/workspace/results/rg-003/analysis-report.json",
  "drift_gate_status": "consistent",
  "success_criteria_status": "met",
  "verdict": "pass",
  "verdict_confidence": "high",
  "next_experiment_action": "phase2-ready",
  "archive_recommended": false,
  "rationale_summary": [
    "The latest run clears the locked success criteria while preserving the anchored claim."
  ],
  "confounders": [],
  "root_causes": [],
  "suggested_actions": [
    {
      "action_id": "act-001",
      "action_type": "phase2-handoff",
      "summary": "Start the conservative Phase 2 paper path around the validated mainline claim.",
      "expected_effect": "Begins writing without expanding scope beyond validated evidence."
    }
  ],
  "decision_options": [
    {
      "option_id": "handoff-001",
      "label": "Start conservative Phase 2 drafting",
      "summary": "Write the paper around the validated mainline claim only.",
      "pros": [
        "Lowest overclaim risk",
        "Fastest path into a reviewable draft"
      ],
      "cons": [
        "Leaves broader framing ideas for later work"
      ],
      "recommended": true,
      "expected_effect": "Preserves the cleanest evidence-to-claim alignment during handoff."
    }
  ],
  "cross_model_review": {
    "used": false,
    "status": "skipped",
    "recommended_verdict": null,
    "notes": "Codex review not requested for this run."
  }
}
```

## Required Fields

- `judge_report_id`
- `project_id`
- `experiment_id`
- `idea_id`
- `branch_id`
- `iteration`
- `generated_at`
- `anchor_path`
- `latest_result_ref`
- `latest_analysis_ref`
- `drift_gate_status`
- `success_criteria_status`
- `verdict`
- `verdict_confidence`
- `next_experiment_action`
- `archive_recommended`
- `rationale_summary`
- `confounders`
- `root_causes`
- `suggested_actions`
- `decision_options`
- `cross_model_review`

## `decision_options[]` Structure

Use when the verdict creates an immediate branch, stop, or human-gated decision, including a `phase2-handoff`.

Each option should contain:

- `option_id`
- `label`
- `summary`
- `pros`
- `cons`
- `recommended`
- `expected_effect`

## Rules

1. `verdict` must match the canonical verdict written to `experiment-memory.md`.
2. `next_experiment_action` must match the canonical next action in `experiment-memory.md`.
3. If a PASS still requires a human-gated publication choice, keep `next_experiment_action: phase2-ready` and store the handoff options in `decision_options`.
4. If branch creation is only a recommendation, record it in `decision_options` and `decision-tree.md`; do not pretend the branch already exists.
5. `cross_model_review` is advisory only and must not contradict canonical state silently.
6. This file must remain machine-parseable JSON.

## Content That Does Not Belong Here

- raw training logs
- copied result ledgers
- hidden edits to current project steering state
- branch history that belongs in `decision-tree.md`
