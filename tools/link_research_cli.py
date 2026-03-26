from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from tools.codex_healthcheck import run_codex_healthcheck
from tools.harness_lint import run_harness_lint
from tools.project_ops import (
    create_project,
    list_projects,
    load_current_project_summary,
    load_runtime_pointer,
    refresh_all_dashboards,
    refresh_project_dashboard,
    write_runtime_pointer,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="link-research")
    subparsers = parser.add_subparsers(dest="command", required=True)

    new_project = subparsers.add_parser("new-project")
    new_project.add_argument("--slug", required=True)
    new_project.add_argument("--title", required=True)
    new_project.add_argument("--owner")

    switch_project = subparsers.add_parser("switch-project")
    switch_project.add_argument("--slug", required=True)

    subparsers.add_parser("list-projects")
    subparsers.add_parser("current-project")
    subparsers.add_parser("codex-healthcheck")
    refresh_dashboard = subparsers.add_parser("refresh-dashboard")
    refresh_target = refresh_dashboard.add_mutually_exclusive_group()
    refresh_target.add_argument("--slug")
    refresh_target.add_argument("--all", action="store_true")
    refresh_target.add_argument("--current", action="store_true")
    subparsers.add_parser("harness-lint")
    return parser


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _safe_print(message: str, stream: object) -> None:
    encoding = getattr(stream, "encoding", None) or "utf-8"
    sanitized = message.encode(encoding, errors="replace").decode(encoding, errors="replace")
    stream.write(sanitized + "\n")


def _handle_new_project(args: argparse.Namespace, repo_root: Path) -> int:
    create_project(
        repo_root=repo_root,
        slug=args.slug,
        title=args.title,
        owner=args.owner,
    )
    print(f"Created project {args.slug} at projects/{args.slug}")
    return 0


def _handle_switch_project(args: argparse.Namespace, repo_root: Path) -> int:
    runtime_state = write_runtime_pointer(repo_root=repo_root, slug=args.slug)
    print(f"Current project set to {runtime_state['current_project_slug']}")
    return 0


def _handle_list_projects(repo_root: Path) -> int:
    summaries = list_projects(repo_root)
    if not summaries:
        print("No live projects found.")
        return 0

    for summary in summaries:
        marker = "*" if summary["is_current"] else "-"
        print(
            f"{marker} {summary['slug']} | {summary['project_title']} | "
            f"{summary['phase']} | {summary['project_status']}"
        )
    return 0


def _handle_harness_lint(repo_root: Path) -> int:
    report = run_harness_lint(repo_root)
    print(f"Harness lint: {report['error_count']} errors, {report['warning_count']} warnings")
    for finding in report["findings"]:
        print(
            f"[{finding['severity'].upper()}] {finding['path']} "
            f"{finding['code']}: {finding['message']}"
        )
    return 0 if report["error_count"] == 0 else 1


def _handle_refresh_dashboard(args: argparse.Namespace, repo_root: Path) -> int:
    if args.all:
        refreshed = refresh_all_dashboards(repo_root)
        if not refreshed:
            print("No live projects found to refresh.")
            return 0
        for item in refreshed:
            print(f"Refreshed dashboard for {item['slug']} -> {item['html_path']}")
        print("Portfolio dashboard -> .link-research/dashboard/index.html")
        return 0

    if args.slug:
        item = refresh_project_dashboard(repo_root, args.slug)
        print(f"Refreshed dashboard for {item['slug']} -> {item['html_path']}")
        return 0

    runtime = load_runtime_pointer(repo_root)
    if runtime is None:
        print(
            "No current project selected. Run new-project, switch-project, or pass --slug.",
            file=sys.stderr,
        )
        return 1

    item = refresh_project_dashboard(repo_root, runtime["current_project_slug"])
    print(f"Refreshed dashboard for {item['slug']} -> {item['html_path']}")
    return 0


def _handle_current_project(repo_root: Path) -> int:
    summary = load_current_project_summary(repo_root)
    if summary is None:
        print(
            "No current project selected. Run: python -m tools.link_research_cli new-project --slug <slug> --title \"<title>\" "
            "or python -m tools.link_research_cli switch-project --slug <slug>",
            file=sys.stderr,
        )
        return 1

    print(f"Current project: {summary['slug']}")
    print(f"Title: {summary['project_title']}")
    print(f"Phase: {summary['phase']}")
    print(f"Status: {summary['project_status']}")
    print(f"Project path: {summary['project_path']}")
    print(f"Decision mode: {summary['decision_mode']}")
    print(f"Decision type: {summary['decision_type'] or 'none'}")
    print(f"Run pointer: {summary['run_pointer_status']}")
    print(f"Active idea: {summary['active_idea_id'] or 'none'}")
    print(f"Active branch: {summary['active_branch_id'] or 'none'}")
    print(f"Current run: {summary['current_run_id'] or 'none'}")
    print(f"Brief ready: {'yes' if summary['brief_ready'] else 'no'}")
    if not summary["brief_ready"]:
        print(f"Missing brief fields: {', '.join(summary['brief_missing_fields'])}")
    if summary["run_status"] is not None:
        print(f"Run status: {summary['run_status']}")
        print(f"Resume safe: {summary['resume_safe']}")
    print(f"Next action: {summary['next_action']}")
    print(f"Suggested Codex prompt: {summary['suggested_prompt']}")
    return 0


def _handle_codex_healthcheck() -> int:
    report = run_codex_healthcheck()
    stream = sys.stdout if report["ok"] else sys.stderr
    _safe_print(report["message"], stream)
    if report.get("detail"):
        _safe_print(report["detail"], stream)
    return 0 if report["ok"] else 1


def main(argv: Sequence[str] | None = None, repo_root: Path | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = repo_root or _default_repo_root()

    try:
        if args.command == "new-project":
            return _handle_new_project(args, root)
        if args.command == "switch-project":
            return _handle_switch_project(args, root)
        if args.command == "list-projects":
            return _handle_list_projects(root)
        if args.command == "current-project":
            return _handle_current_project(root)
        if args.command == "codex-healthcheck":
            return _handle_codex_healthcheck()
        if args.command == "refresh-dashboard":
            return _handle_refresh_dashboard(args, root)
        if args.command == "harness-lint":
            return _handle_harness_lint(root)
        parser.error(f"Unsupported command: {args.command}")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
