# Recovery And Resume

Use this guide when a session was interrupted and you need to resume without guessing.

## 1. Check the selected project

Run:

```bash
python -m tools.link_research_cli current-project
```

If no project is selected, switch first:

```bash
python -m tools.link_research_cli new-project --slug <slug> --title "<title>"
python -m tools.link_research_cli switch-project --slug <slug>
```

## 2. Read the canonical posture

The recovery command summarizes the same files Codex should trust:

- `projects/<slug>/STATE.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/review-state.json`

If you need more detail, open those files directly instead of relying on memory.

## 3. Choose the right resume action

Typical cases:

- `phase0` with no active idea:
  - if the brief is incomplete, finish `project-brief.md` before starting Phase 1 bootstrap
  - otherwise resume Phase 1 bootstrap from `project-brief.md`
- active run with `running` or `paused` status and `resume_safe: true`:
  - ask Codex to inspect `review-state.json` and resume that run safely
- `project_status: waiting-human` or run `status: waiting-human`:
  - review the pending human-gated decision first; do not auto-resume
- `next_experiment_action: phase2-ready` with no active `phase2-handoff` decision:
  - ask Codex to verify the evidence trail and start Phase 2
- stale `current_run_id` versus `review-state.json.run_id`:
  - stop and reconcile the mismatch before resuming any execution
- everything else:
  - ask Codex to continue from `STATE.md.next_action`

## 4. Resume with a concrete prompt

Recommended template:

```text
Read projects/<slug>/STATE.md, experiment-memory.md, and review-state.json. Summarize the current posture, explain whether it is safe to resume, and continue from the recorded next action without rewriting prior evidence.
```

## 5. Avoid messy recovery

Do not resume by intuition alone. Before asking Codex to continue, make sure:

- the selected project slug is correct
- the current run id matches the intended run
- the next action still matches the evidence
- any required human decision is explicit

This keeps resume behavior conservative, auditable, and much less likely to drift.
