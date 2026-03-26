from __future__ import annotations

from dataclasses import dataclass

from tools.codex_healthcheck import _default_command_runner, run_codex_healthcheck


@dataclass
class FakeCompletedProcess:
    returncode: int
    stdout: str = ""
    stderr: str = ""


def test_codex_healthcheck_reports_success_when_codex_and_gpt_are_healthy():
    def runner(args: list[str]) -> FakeCompletedProcess:
        if args[:2] == ["codex", "--version"]:
            return FakeCompletedProcess(returncode=0, stdout="codex 1.0.0\n")
        if args[:4] == ["codex", "exec", "-m", "gpt-5.4"]:
            return FakeCompletedProcess(returncode=0, stdout="GPT54_OK\n")
        raise AssertionError(f"Unexpected command: {args}")

    report = run_codex_healthcheck(command_runner=runner)

    assert report["ok"] is True
    assert report["stage"] == "ok"


def test_codex_healthcheck_reports_missing_codex_binary():
    def runner(args: list[str]) -> FakeCompletedProcess:
        if args[:2] == ["codex", "--version"]:
            raise FileNotFoundError("codex")
        raise AssertionError(f"Unexpected command: {args}")

    report = run_codex_healthcheck(command_runner=runner)

    assert report["ok"] is False
    assert report["stage"] == "codex-missing"


def test_codex_healthcheck_treats_shell_command_not_found_as_missing_codex():
    def runner(args: list[str]) -> FakeCompletedProcess:
        if args[:2] == ["codex", "--version"]:
            return FakeCompletedProcess(
                returncode=1,
                stderr="'codex' is not recognized as an internal or external command",
            )
        raise AssertionError(f"Unexpected command: {args}")

    report = run_codex_healthcheck(command_runner=runner)

    assert report["ok"] is False
    assert report["stage"] == "codex-missing"


def test_codex_healthcheck_reports_broken_codex_cli_invocation():
    def runner(args: list[str]) -> FakeCompletedProcess:
        if args[:2] == ["codex", "--version"]:
            return FakeCompletedProcess(returncode=2, stderr="unknown option")
        raise AssertionError(f"Unexpected command: {args}")

    report = run_codex_healthcheck(command_runner=runner)

    assert report["ok"] is False
    assert report["stage"] == "codex-cli-failed"


def test_codex_healthcheck_treats_exec_shell_command_not_found_as_missing_codex():
    def runner(args: list[str]) -> FakeCompletedProcess:
        if args[:2] == ["codex", "--version"]:
            return FakeCompletedProcess(returncode=0, stdout="codex 1.0.0\n")
        if args[:4] == ["codex", "exec", "-m", "gpt-5.4"]:
            return FakeCompletedProcess(returncode=1, stderr="/bin/sh: codex: command not found")
        raise AssertionError(f"Unexpected command: {args}")

    report = run_codex_healthcheck(command_runner=runner)

    assert report["ok"] is False
    assert report["stage"] == "codex-missing"


def test_codex_healthcheck_reports_gpt_call_failure():
    def runner(args: list[str]) -> FakeCompletedProcess:
        if args[:2] == ["codex", "--version"]:
            return FakeCompletedProcess(returncode=0, stdout="codex 1.0.0\n")
        if args[:4] == ["codex", "exec", "-m", "gpt-5.4"]:
            return FakeCompletedProcess(returncode=1, stderr="provider timeout")
        raise AssertionError(f"Unexpected command: {args}")

    report = run_codex_healthcheck(command_runner=runner)

    assert report["ok"] is False
    assert report["stage"] == "gpt-call-failed"


def test_codex_healthcheck_reports_gpt_token_mismatch():
    def runner(args: list[str]) -> FakeCompletedProcess:
        if args[:2] == ["codex", "--version"]:
            return FakeCompletedProcess(returncode=0, stdout="codex 1.0.0\n")
        if args[:4] == ["codex", "exec", "-m", "gpt-5.4"]:
            return FakeCompletedProcess(returncode=0, stdout="unexpected-output\n")
        raise AssertionError(f"Unexpected command: {args}")

    report = run_codex_healthcheck(command_runner=runner)

    assert report["ok"] is False
    assert report["stage"] == "gpt-token-mismatch"


def test_default_command_runner_uses_utf8_safe_decoding(monkeypatch):
    captured: dict[str, object] = {}

    def fake_run(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return FakeCompletedProcess(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("tools.codex_healthcheck.subprocess.run", fake_run)

    _default_command_runner(["codex", "--version"])

    assert captured["kwargs"]["text"] is True
    assert captured["kwargs"]["encoding"] == "utf-8"
    assert captured["kwargs"]["errors"] == "replace"
