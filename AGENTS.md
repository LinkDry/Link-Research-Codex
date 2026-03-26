# Link-Research-Codex Agent Entry

This repository is Codex-driven. Use this file as the repo-discovery entrypoint for Codex-compatible agents, and treat [Agent.md](Agent.md) as the fuller operator contract.

## Core Rules

- Codex is the primary operator and sole owner of canonical project state.
- Canonical state lives in `projects/<slug>/STATE.md`, `projects/<slug>/experiment-memory.md`, `projects/<slug>/review-state.json`, and `projects/<slug>/results.tsv`.
- Derived dashboard files under `projects/<slug>/workspace/` are never source of truth.
- Use repo-local CLI commands when the user's intent is clear: `current-project`, `list-projects`, `refresh-dashboard`, `harness-lint`, and `codex-healthcheck`.
- GPT-5.4 review is optional and advisory only through Codex execution; it must not silently overwrite canonical project files.
- Pause for operator input only when a decision is irreversible, integrity-sensitive, high-cost, or explicitly marked `human-gated` in canonical state.

## Primary References

- Full operator contract: [Agent.md](Agent.md)
- Quickstart: `docs/guides/phase1-quickstart.md`
- Recovery: `docs/guides/recovery-and-resume.md`
- Dashboard: `docs/guides/dashboard-usage.md`
- Skills: `skills/*/SKILL.md`
