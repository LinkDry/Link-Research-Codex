# Link-Research-Codex

Schema-first research steering for a Codex-driven paper workflow.

Canonical project state lives in project files, dashboard data is derived, and operator tooling is available through repo-local commands instead of prose-only rituals.

## Codex-first Usage

Codex is the primary operator. This is a Codex-first repository, so in normal use you should not need to remember the repo CLI or manually run support scripts just to keep research moving.

The intended interaction model is:

- you give Codex a direction, seed papers, or a short steering instruction
- Codex decides when to run low-risk repo commands like `current-project`, `refresh-dashboard`, `list-projects`, `harness-lint`, or `codex-healthcheck`
- Codex only pauses when a decision is high-impact, integrity-sensitive, expensive, or irreversible
- when Codex does pause, it should present a small choice set with a recommendation rather than forcing a long freeform reply

## Codex And GPT-5.4 Roles

Codex is the primary operator across the whole paper pipeline.

GPT-5.4 enters as an optional strict-review lane through isolated Codex execution at selected high-value checkpoints rather than as a second hidden owner of project state.

The intended advisory review touchpoints are:

- `novelty-check` for idea quality, novelty overclaim risk, and primary-line selection quality
- `experiment-plan` for falsifiability, baselines, metrics, confounders, and execution risk
- `drift-detector` for drift-score sanity checks
- `judge` for conservative Phase 1 verdict review
- `phase2-publish` for claims-evidence traceability and publication-time integrity review
- `overnight` only indirectly, when it routes into one of the skills above

Review-lane output is advisory only. Canonical project truth still lives in the project files and is ultimately written by the owning skill.

## Codex Setup

This repository does not commit machine-specific API keys, proxy secrets, or Codex auth state.

To make the Codex -> GPT-5.4 review path work on a fresh machine:

1. Configure Codex in `~/.codex/config.toml` plus `~/.codex/auth.json` (or the equivalent `CODEX_HOME`) so normal Codex execution succeeds against your intended provider or proxy.
2. Verify the local CLI is reachable:

```bash
codex --version
```

3. Verify GPT-5.4 is reachable:

```bash
codex exec -m gpt-5.4 "Reply with exactly: GPT54_OK"
```

4. Run the repo-local end-to-end healthcheck:

```bash
python -m tools.link_research_cli codex-healthcheck
```

If you use cc-switch or any other proxy layer, make sure Codex is pointed at the intended routing setup. This repo assumes those user-scope settings already exist; it does not override them locally.

## Quickstart

Create a live project from the canonical scaffold:

Project slugs must use lowercase letters, numbers, and hyphens only.

```bash
python -m tools.link_research_cli new-project --slug demo-project --title "Demo Project"
```

Set the current project pointer used by local operator tooling:

```bash
python -m tools.link_research_cli switch-project --slug demo-project
```

Inspect the currently selected project and get a suggested next Codex prompt:

```bash
python -m tools.link_research_cli current-project
```

Refresh the derived dashboard files for the current project:

```bash
python -m tools.link_research_cli refresh-dashboard
```

Refresh all live project dashboards and regenerate the repo-local portfolio page:

```bash
python -m tools.link_research_cli refresh-dashboard --all
```

List live projects:

```bash
python -m tools.link_research_cli list-projects
```

Run the current harness contract checks:

```bash
python -m tools.link_research_cli harness-lint
```

Run the Codex -> GPT-5.4 healthcheck:

```bash
python -m tools.link_research_cli codex-healthcheck
```

Run the tooling test suite:

```bash
pytest -q
```

## Operator Flow

For the real day-1 path into Phase 1, use:

- `docs/guides/phase1-quickstart.md`
- `docs/guides/recovery-and-resume.md`
- `docs/guides/dashboard-usage.md`
- `Agent.md`

The intended operator loop is:

1. Create a project.
2. Switch to it.
3. Fill `projects/<slug>/project-brief.md`.
4. Ask Codex to begin Phase 1 bootstrap.
5. Use `python -m tools.link_research_cli current-project` whenever you need a fast recovery summary.
6. Use `python -m tools.link_research_cli refresh-dashboard` whenever you want a fresh dashboard snapshot and HTML view.
7. Use `.link-research/dashboard/index.html` after `refresh-dashboard --all` when you want a repo-local portfolio overview.

## Runtime Notes

- A fresh clone does not automatically enable the GPT review lane. The repo provides the skill contracts; your user-scope Codex setup makes those contracts executable.
- If Codex emits local sqlite migration warnings, the issue is in local runtime state under `CODEX_HOME`, not in the repo checkout.

## Notes

- Current active docs are:
  - `docs/guides/`
  - `docs/policies/`
  - `docs/schema/`
  - `docs/views/`
  - root `skills/*/SKILL.md`
- `scaffold/project/` is the canonical scaffold and repo fixture source for new projects.
- `projects/` is reserved for live projects only.
- `.link-research/runtime.json` is local operator convenience state, not canonical research state.
- `projects/<slug>/workspace/dashboard-data.json` is derived and should be regenerated from canonical files rather than edited as source of truth.
