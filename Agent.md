# Link-Research-Codex

Codex is the default operator for this repository. Keep work grounded in the canonical project files and the repo-local CLI rather than relying on conversational memory.

## First Moves

1. Run `python -m tools.link_research_cli current-project`.
2. If no project is selected, create or switch one with:
   - `python -m tools.link_research_cli new-project --slug <slug> --title "<title>"`
   - `python -m tools.link_research_cli switch-project --slug <slug>`
3. Read the selected project's canonical state:
   - `projects/<slug>/STATE.md`
   - `projects/<slug>/experiment-memory.md`
   - `projects/<slug>/review-state.json`

## Operator Surface

- Quickstart: `docs/guides/phase1-quickstart.md`
- Resume and recovery: `docs/guides/recovery-and-resume.md`
- Dashboard usage: `docs/guides/dashboard-usage.md`
- Optional history context: `docs/history-summary.md`
- Project scaffold source: `scaffold/project/`
- Research skills: `skills/*/SKILL.md`

## GPT-5.4 Review Lane

- Codex is the primary operator and sole owner of canonical project state.
- When you want an extra strict review pass, Codex may invoke an isolated GPT-5.4 check at selected checkpoints.
- Current advisory review touchpoints are `novelty-check`, `experiment-plan`, `drift-detector`, `judge`, and `phase2-publish`.
- These reviews are advisory only. They should harden novelty screening, experiment design, drift review, and publication accuracy, but they must not silently overwrite canonical project files on their own.
- For a repo-local end-to-end check, run `python -m tools.link_research_cli codex-healthcheck`.

## Default Operator Contract

- Treat short user intent as enough to choose and run the repo-local CLI when the action is low-risk and reversible.
- Do not ask the user to memorize or manually invoke routine scripts when Codex can safely run them instead.
- After any CLI action that changes the active project or derived views, reread the canonical state or run `current-project` before steering the next step.
- Ask only when a required argument is missing or the next action is expensive, irreversible, or integrity-sensitive.

## Tool Autonomy Map

Codex should normally execute these directly when the user's intent is clear:

- "show current status" -> `python -m tools.link_research_cli current-project`
- "list my projects" -> `python -m tools.link_research_cli list-projects`
- "refresh the dashboard" -> `python -m tools.link_research_cli refresh-dashboard`
- "refresh all dashboards" -> `python -m tools.link_research_cli refresh-dashboard --all`
- "check the harness structure" -> `python -m tools.link_research_cli harness-lint`
- "check GPT reviewer health" -> `python -m tools.link_research_cli codex-healthcheck`
- "create a new project" with explicit slug and title -> `python -m tools.link_research_cli new-project ...` followed by `switch-project`
- "switch to project <slug>" -> `python -m tools.link_research_cli switch-project --slug <slug>`

Pause first for actions such as archive decisions, destructive cleanup, remote experiment spend, or any change that would rewrite research direction rather than inspect or summarize it.

## Canonical Rules

- `STATE.md` is the compact project steering view.
- `experiment-memory.md` is the active experiment-line view.
- `review-state.json` is the resumable run controller.
- `results.tsv` is append-only evidence.
- `projects/<slug>/workspace/dashboard-data.json` and `projects/<slug>/workspace/dashboard.html` are derived views, never source of truth.

## Execution Posture

- Prefer automation by default when the state remains `auto` or `auto-report`.
- Pause for operator input when the canonical state is `human-gated`, when integrity is at risk, or when a decision is irreversible.
- When unsure, trust the recorded next action and referenced evidence before inventing a new path.

## Choice-First Human Input

- Most day-to-day turns should not require long freeform user messages.
- When Codex needs operator input, present 2-4 concrete options with one recommended default.
- Each option should state what Codex will do next and the main tradeoff.
- Always leave room for a custom instruction if none of the listed options fit.

## Useful Commands

- `python -m tools.link_research_cli list-projects`
- `python -m tools.link_research_cli current-project`
- `python -m tools.link_research_cli refresh-dashboard`
- `python -m tools.link_research_cli refresh-dashboard --all`
- `python -m tools.link_research_cli harness-lint`
- `python -m tools.link_research_cli codex-healthcheck`

## Maintenance

- Use `scaffold/project/` as the canonical seed for new projects and fixture validation.
- Route live work through `docs/guides/`, `docs/policies/`, `docs/schema/`, `docs/views/`, and root `skills/*/SKILL.md`.
- Treat `docs/history-summary.md` as optional background only, not as an active operator spec.
