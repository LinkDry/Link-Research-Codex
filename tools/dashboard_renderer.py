from __future__ import annotations

import html
import json
from typing import Any


def _escape(value: Any) -> str:
    if value is None:
        return "none"
    if isinstance(value, list):
        return ", ".join(_escape(item) for item in value) if value else "none"
    return html.escape(str(value))


def _render_kv(label: str, value: Any) -> str:
    return (
        '<div class="kv-row">'
        f'<span class="kv-label">{html.escape(label)}</span>'
        f'<span class="kv-value">{_escape(value)}</span>'
        "</div>"
    )


def _render_list_card(title: str, items: list[dict[str, Any]], fields: list[tuple[str, str]]) -> str:
    body_parts = [f"<h3>{html.escape(title)}</h3>"]
    if not items:
        body_parts.append('<p class="empty">No current signals.</p>')
    else:
        body_parts.append('<div class="list-block">')
        for item in items[:5]:
            body_parts.append('<article class="list-item">')
            for label, key in fields:
                body_parts.append(_render_kv(label, item.get(key)))
            body_parts.append("</article>")
        body_parts.append("</div>")
    return f'<section class="panel memory-card">{"".join(body_parts)}</section>'


def render_dashboard_html(slug: str, dashboard: dict[str, Any]) -> str:
    project = dashboard["project"]
    experiment = dashboard["experiment"]
    run = dashboard["run"]
    memory = dashboard["memory"]
    meta = dashboard["meta"]

    title = project.get("project_title") or slug
    data_blob = json.dumps(dashboard, indent=2).replace("</", "<\\/")

    steering_rows = "".join(
        [
            _render_kv("Project ID", project.get("project_id")),
            _render_kv("Phase", project.get("phase")),
            _render_kv("Status", project.get("project_status")),
            _render_kv("Risk", project.get("risk_level")),
            _render_kv("Decision Mode", project.get("decision_mode")),
            _render_kv("Decision Type", project.get("decision_type")),
            _render_kv("Human Attention", project.get("human_attention")),
            _render_kv("Active Idea", project.get("active_idea_id")),
            _render_kv("Active Branch", project.get("active_branch_id")),
            _render_kv("Blockers", project.get("blockers")),
        ]
    )
    experiment_rows = "".join(
        [
            _render_kv("Experiment ID", experiment.get("experiment_id")),
            _render_kv("Idea", experiment.get("idea_id")),
            _render_kv("Branch", experiment.get("branch_id")),
            _render_kv("Status", experiment.get("status")),
            _render_kv("Latest Verdict", experiment.get("latest_judge_verdict")),
            _render_kv("Latest Drift Score", experiment.get("latest_drift_score")),
            _render_kv("Next Experiment Action", experiment.get("next_experiment_action")),
        ]
    )
    run_rows = "".join(
        [
            _render_kv("Run ID", run.get("run_id")),
            _render_kv("Run Status", run.get("status")),
            _render_kv("Current Step", run.get("current_step_name")),
            _render_kv("Resume Safe", run.get("resume_safe")),
            _render_kv("Human Attention", run.get("human_attention")),
            _render_kv("Blocking Reason", run.get("blocking_reason")),
        ]
    )

    memory_cards = "".join(
        [
            _render_list_card(
                "Recent Lessons",
                memory.get("recent_lessons", []),
                [("Lesson", "lesson_id"), ("Summary", "summary"), ("Category", "category")],
            ),
            _render_list_card(
                "Active Patterns",
                memory.get("active_patterns", []),
                [("Pattern", "pattern_id"), ("Summary", "summary"), ("Action", "recommended_action")],
            ),
            _render_list_card(
                "Open Capability Gaps",
                memory.get("open_capability_gaps", []),
                [("Gap", "gap_id"), ("Description", "description"), ("Impact", "impact_level")],
            ),
            _render_list_card(
                "Recent Failure Warnings",
                memory.get("recent_warnings", []),
                [("Failure", "failure_id"), ("Class", "failure_class"), ("Summary", "summary")],
            ),
        ]
    )

    next_action = _escape(project.get("next_action"))
    decision_callout = ""
    if project.get("decision_type"):
        decision_callout = (
            '<div class="callout">'
            f"<strong>Pending decision:</strong> {_escape(project.get('decision_type'))}"
            "</div>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} Dashboard</title>
  <style>
    :root {{
      --bg: #f3efe5;
      --bg-accent: #e7dfcf;
      --ink: #1d2623;
      --muted: #5d6a64;
      --panel: rgba(255, 252, 247, 0.88);
      --line: rgba(29, 38, 35, 0.12);
      --hero: linear-gradient(135deg, #f0d7b5 0%, #d8e4d1 55%, #bdd8d4 100%);
      --shadow: 0 18px 40px rgba(51, 63, 58, 0.12);
      --accent: #8f4f2a;
      --accent-soft: #efdfd2;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top right, rgba(143, 79, 42, 0.08), transparent 30%),
        linear-gradient(180deg, var(--bg) 0%, var(--bg-accent) 100%);
    }}
    .shell {{
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }}
    .hero {{
      background: var(--hero);
      border: 1px solid var(--line);
      border-radius: 28px;
      padding: 28px;
      box-shadow: var(--shadow);
      position: relative;
      overflow: hidden;
    }}
    .hero::after {{
      content: "";
      position: absolute;
      inset: auto -40px -50px auto;
      width: 180px;
      height: 180px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.35);
      filter: blur(10px);
    }}
    .eyebrow {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.16em;
      color: var(--muted);
      margin-bottom: 12px;
    }}
    h1, h2, h3 {{
      font-family: "Alegreya", Georgia, serif;
      margin: 0;
    }}
    h1 {{
      font-size: clamp(34px, 4vw, 52px);
      line-height: 1;
      margin-bottom: 10px;
    }}
    .hero-subtitle {{
      max-width: 720px;
      font-size: 15px;
      color: var(--muted);
      margin: 0 0 16px;
    }}
    .badge-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .badge {{
      border-radius: 999px;
      padding: 8px 12px;
      background: rgba(255, 255, 255, 0.72);
      border: 1px solid rgba(29, 38, 35, 0.08);
      font-size: 13px;
    }}
    .callout {{
      margin-top: 16px;
      padding: 14px 16px;
      border-radius: 18px;
      background: var(--accent-soft);
      border: 1px solid rgba(143, 79, 42, 0.14);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 18px;
      margin-top: 20px;
    }}
    .panel {{
      grid-column: span 4;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 22px;
      padding: 20px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(8px);
    }}
    .panel h2 {{
      font-size: 26px;
      margin-bottom: 16px;
    }}
    .panel h3 {{
      font-size: 22px;
      margin-bottom: 12px;
    }}
    .kv-row {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 0;
      border-bottom: 1px solid var(--line);
      align-items: flex-start;
    }}
    .kv-row:last-child {{
      border-bottom: none;
    }}
    .kv-label {{
      color: var(--muted);
      font-size: 13px;
      width: 42%;
      flex: 0 0 42%;
    }}
    .kv-value {{
      font-size: 14px;
      text-align: right;
      width: 58%;
      flex: 0 0 58%;
      word-break: break-word;
    }}
    .memory-shell {{
      margin-top: 24px;
    }}
    .memory-shell h2 {{
      font-size: 30px;
      margin: 0 0 16px;
      padding-left: 4px;
    }}
    .memory-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }}
    .memory-card {{
      box-shadow: none;
    }}
    .list-item {{
      padding: 12px 0;
      border-top: 1px solid var(--line);
    }}
    .list-item:first-child {{
      border-top: none;
      padding-top: 0;
    }}
    .empty {{
      color: var(--muted);
      margin: 0;
    }}
    .next-action {{
      margin-top: 16px;
      padding: 16px;
      border-radius: 18px;
      background: rgba(29, 38, 35, 0.06);
      border: 1px solid rgba(29, 38, 35, 0.08);
    }}
    .footer {{
      margin-top: 20px;
      color: var(--muted);
      font-size: 13px;
      display: flex;
      justify-content: space-between;
      gap: 18px;
      flex-wrap: wrap;
    }}
    @media (max-width: 980px) {{
      .panel {{
        grid-column: span 12;
      }}
      .memory-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div class="eyebrow">Link-Research Dashboard</div>
      <h1>{html.escape(title)}</h1>
      <p class="hero-subtitle">Current Steering for <code>projects/{html.escape(slug)}</code></p>
      <div class="badge-row">
        <span class="badge">Phase: {_escape(project.get("phase"))}</span>
        <span class="badge">Status: {_escape(project.get("project_status"))}</span>
        <span class="badge">Risk: {_escape(project.get("risk_level"))}</span>
        <span class="badge">Generated: {_escape(meta.get("generated_at"))}</span>
      </div>
      <div class="next-action">
        <strong>Next action:</strong> {next_action}
      </div>
      {decision_callout}
    </section>

    <section class="grid">
      <section class="panel">
        <h2>Current Steering</h2>
        {steering_rows}
      </section>
      <section class="panel">
        <h2>Active Experiment</h2>
        {experiment_rows}
      </section>
      <section class="panel">
        <h2>Live Run</h2>
        {run_rows}
      </section>
    </section>

    <section class="memory-shell">
      <h2>Memory Signals</h2>
      <div class="memory-grid">
        {memory_cards}
      </div>
    </section>

    <footer class="footer">
      <span>Derived from canonical project files. Do not edit this dashboard as source of truth.</span>
      <span>Schema: {_escape(meta.get("schema_version"))}</span>
    </footer>
  </main>
  <script id="dashboard-data" type="application/json">{data_blob}</script>
</body>
</html>
"""


def render_portfolio_html(projects: list[dict[str, Any]]) -> str:
    cards: list[str] = []
    for project in projects:
        current_badge = '<span class="status-badge">Current focus</span>' if project.get("is_current") else ""
        dashboard_path = project.get("dashboard_path", "")
        dashboard_href = f"../../{dashboard_path}" if dashboard_path else "#"
        cards.append(
            f"""
            <article class="project-card">
              <div class="card-top">
                <div>
                  <p class="slug">{html.escape(project.get("slug", ""))}</p>
                  <h2>{html.escape(project.get("project_title", project.get("slug", "")))}</h2>
                </div>
                {current_badge}
              </div>
              <div class="meta-row">
                <span>Phase: {_escape(project.get("phase"))}</span>
                <span>Status: {_escape(project.get("project_status"))}</span>
                <span>Risk: {_escape(project.get("risk_level"))}</span>
              </div>
              <p class="next-action"><strong>Next:</strong> {_escape(project.get("next_action"))}</p>
              <p class="path-label">Dashboard: <code>{html.escape(dashboard_path)}</code></p>
              <a class="dashboard-link" href="{html.escape(dashboard_href)}">Open project dashboard</a>
            </article>
            """
        )

    if not cards:
        cards.append('<p class="empty">No live projects found. Create one with <code>new-project</code>.</p>')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Research Portfolio</title>
  <style>
    :root {{
      --bg: #f4f1ea;
      --ink: #1f2724;
      --muted: #5e6b65;
      --card: rgba(255, 252, 248, 0.9);
      --line: rgba(31, 39, 36, 0.12);
      --accent: #365c54;
      --accent-soft: rgba(54, 92, 84, 0.12);
      --shadow: 0 18px 40px rgba(52, 66, 61, 0.1);
      --hero: linear-gradient(135deg, #f0dec0 0%, #d1e2da 52%, #c4d6e6 100%);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(54, 92, 84, 0.08), transparent 28%),
        linear-gradient(180deg, var(--bg) 0%, #ebe3d6 100%);
    }}
    .shell {{
      width: min(1120px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }}
    .hero {{
      background: var(--hero);
      border-radius: 28px;
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
      padding: 28px;
      margin-bottom: 22px;
    }}
    .eyebrow {{
      margin: 0 0 12px;
      font-size: 12px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    h1, h2 {{
      font-family: "Alegreya", Georgia, serif;
      margin: 0;
    }}
    h1 {{
      font-size: clamp(34px, 4vw, 52px);
      line-height: 1;
      margin-bottom: 10px;
    }}
    .hero-copy {{
      margin: 0;
      max-width: 760px;
      color: var(--muted);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 18px;
    }}
    .project-card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 22px;
      box-shadow: var(--shadow);
      padding: 20px;
    }}
    .card-top {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-start;
    }}
    .slug {{
      margin: 0 0 6px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-size: 12px;
      color: var(--muted);
    }}
    .status-badge {{
      border-radius: 999px;
      padding: 8px 12px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 12px;
      white-space: nowrap;
    }}
    .meta-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 14px 0 12px;
      color: var(--muted);
      font-size: 13px;
    }}
    .next-action {{
      margin: 0 0 14px;
    }}
    .path-label {{
      color: var(--muted);
      font-size: 13px;
      margin: 0 0 14px;
      word-break: break-word;
    }}
    .dashboard-link {{
      display: inline-flex;
      text-decoration: none;
      padding: 10px 14px;
      border-radius: 999px;
      background: var(--accent);
      color: white;
    }}
    .empty {{
      color: var(--muted);
      margin: 0;
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <p class="eyebrow">Link-Research Portfolio</p>
      <h1>Research Portfolio</h1>
      <p class="hero-copy">Repo-local overview of live projects and their per-project dashboards. This page is derived and can be regenerated at any time.</p>
    </section>
    <section class="grid">
      {''.join(cards)}
    </section>
  </main>
</body>
</html>
"""
