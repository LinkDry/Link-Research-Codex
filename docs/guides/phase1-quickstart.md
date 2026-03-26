# Phase 1 Quickstart

This guide is the shortest reliable path from a fresh repo checkout to a live Phase 1 project.

## 1. Create and select a project

```bash
python -m tools.link_research_cli new-project --slug demo-project --title "Demo Project"
python -m tools.link_research_cli switch-project --slug demo-project
python -m tools.link_research_cli current-project
```

The last command confirms which project Codex should operate on and shows the next suggested prompt.

Project slugs must use lowercase letters, numbers, and hyphens only.

## 2. Fill the project brief

Open `projects/<slug>/project-brief.md` and fill the intake fields before asking Codex to start work.

Use one of the two supported intake modes:

- `direction-search`: give Codex a research direction and let it search literature for promising novelty.
- `seed-papers`: provide one or more seed papers so Codex can propose tighter idea branches from a bounded context.

Keep the brief concrete. A good brief defines the target domain, constraints, evaluation preferences, and any hard exclusions.

## 3. Start Phase 1 bootstrap

Once the brief is filled, ask Codex to:

- read `projects/<slug>/project-brief.md`
- inspect `projects/<slug>/STATE.md`
- begin Phase 1 bootstrap

Recommended operator prompt:

```text
Read projects/<slug>/project-brief.md and the canonical Phase 1 state files, then begin Phase 1 bootstrap. Choose the correct intake mode, produce the first literature review pass, and propose the first idea candidates without drifting away from the brief.
```

## 4. Watch the canonical files

During Phase 1, treat these files as the main truth surface:

- `projects/<slug>/STATE.md`
- `projects/<slug>/experiment-memory.md`
- `projects/<slug>/review-state.json`

Use `python -m tools.link_research_cli current-project` whenever you want a compact summary instead of manually opening all three.

If you want to verify the Codex -> GPT-5.4 review path from the repo entrypoint, run:

```bash
python -m tools.link_research_cli codex-healthcheck
```

When the review lane is available, Codex may also run a GPT-5.4 advisory pass during `novelty-check`, `experiment-plan`, `drift-detector`, and `judge`. Those reviews are there to make the line more conservative, not to replace canonical state ownership.

## 5. When to intervene

Most iterations should stay automated. Step in when:

- Codex reports a major branch or archive decision
- evidence no longer supports the original idea
- a run is blocked and asks for a human choice
- you want to redirect the research objective itself

When you do intervene, prefer explicit instructions tied to the canonical files rather than conversational guesses.

## 6. Low-Typing Operator Mode

Once the project is bootstrapped, the preferred workflow is short-intent steering rather than manual script operation.

Codex should infer and run routine repo commands for you when intent is clear, for example:

- "Show me where the current project stands." -> run `current-project`
- "Refresh the dashboard." -> run `refresh-dashboard`
- "Check whether the harness structure is still healthy." -> run `harness-lint`
- "Switch to project <slug> and resume safely." -> run `switch-project`, then inspect canonical state

Only high-impact decisions should require a pause. When Codex does pause, it should offer a small set of concrete options, recommend one, and let you override with a custom reply if needed.
