# Dashboard Usage

The dashboard is a derived steering view, not a source of truth.

## Canonical vs Derived

The dashboard summarizes:

- `projects/<slug>/STATE.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/review-state.json`
- `memory/lessons-learned.md`
- `memory/failure-library.md`

If the dashboard and canonical files disagree, trust the canonical files and refresh the dashboard.

## Refresh The Dashboard

For the current selected project:

```bash
python -m tools.link_research_cli refresh-dashboard
```

For a specific project:

```bash
python -m tools.link_research_cli refresh-dashboard --slug <slug>
```

For all live projects:

```bash
python -m tools.link_research_cli refresh-dashboard --all
```

Running `--all` also writes a repo-local portfolio overview to:

- `.link-research/dashboard/index.html`

That portfolio page is intentionally local convenience state, so it can be regenerated freely without becoming project truth.

## Output Files

Refreshing writes:

- `projects/<slug>/workspace/dashboard-data.json`
- `projects/<slug>/workspace/dashboard.html`
- `.link-research/dashboard/index.html` when `--all` is used

`dashboard-data.json` is the machine-friendly projection.

`dashboard.html` is the operator-facing shell you can open directly.

## Recommended Operator Loop

1. Use `current-project` to check steering posture and suggested next prompt.
2. Run or resume work through Codex.
3. Refresh the dashboard when you want a cleaner visual summary.
4. If a human-gated decision appears, review the canonical files before acting.
5. Use the portfolio page when you need a multi-project dashboard rather than a single-project view.

## Safety Rule

Do not edit `dashboard-data.json` or `dashboard.html` as if they were canonical state. Regenerate them from the real project files instead.
