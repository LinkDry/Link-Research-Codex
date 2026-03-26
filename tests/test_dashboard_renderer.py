from tools.dashboard_renderer import render_dashboard_html, render_portfolio_html


def test_render_dashboard_html_includes_core_sections():
    dashboard = {
        "meta": {
            "generated_at": "2026-03-25T12:00:00+08:00",
            "schema_version": "schema-2026-03",
            "is_derived": True,
        },
        "project": {
            "project_id": "proj-demo",
            "project_title": "Demo Project",
            "phase": "phase1",
            "project_status": "running",
            "next_action": "Run the next validation iteration.",
            "risk_level": "medium",
            "decision_mode": "auto-report",
            "decision_type": None,
            "human_attention": "none",
            "active_idea_id": "idea-demo",
            "active_branch_id": "branch-a",
            "blockers": [],
        },
        "experiment": {
            "experiment_id": "exp-001",
            "status": "analyzed",
            "latest_judge_verdict": "tweak",
            "latest_drift_score": 2.5,
            "next_experiment_action": "rerun",
            "idea_id": "idea-demo",
            "branch_id": "branch-a",
        },
        "run": {
            "run_id": "run-001",
            "status": "running",
            "current_step_name": "analyze-results",
            "human_attention": "none",
            "resume_safe": True,
            "blocking_reason": None,
        },
        "memory": {
            "recent_lessons": [{"lesson_id": "lesson-001", "summary": "Metric leaked task difficulty."}],
            "active_patterns": [{"pattern_id": "pattern-001", "summary": "Tiny evals hide regressions."}],
            "open_capability_gaps": [{"gap_id": "gap-001", "description": "Need automated ablation summaries."}],
            "recent_warnings": [{"failure_id": "failure-001", "summary": "Broader split collapsed performance."}],
        },
    }

    html = render_dashboard_html("demo-project", dashboard)

    assert "Demo Project" in html
    assert "Current Steering" in html
    assert "Memory Signals" in html
    assert "Metric leaked task difficulty." in html
    assert '<script id="dashboard-data" type="application/json">' in html
    assert "Derived from canonical project files" in html
    assert "Link-Research V2 Dashboard" not in html


def test_render_portfolio_html_marks_current_project():
    html = render_portfolio_html(
        [
            {
                "slug": "demo-project",
                "project_title": "Demo Project",
                "phase": "phase1",
                "project_status": "running",
                "risk_level": "medium",
                "next_action": "Analyze results",
                "is_current": True,
                "dashboard_path": "projects/demo-project/workspace/dashboard.html",
            },
            {
                "slug": "second-project",
                "project_title": "Second Project",
                "phase": "phase0",
                "project_status": "idle",
                "risk_level": "low",
                "next_action": "Fill project brief",
                "is_current": False,
                "dashboard_path": "projects/second-project/workspace/dashboard.html",
            },
        ]
    )

    assert "Research Portfolio" in html
    assert "Demo Project" in html
    assert "Current focus" in html
    assert "projects/demo-project/workspace/dashboard.html" in html
    assert "Link-Research V2 Portfolio" not in html
