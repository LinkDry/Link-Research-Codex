from __future__ import annotations

import os
import subprocess
from typing import Any, Callable


CommandRunner = Callable[[list[str]], Any]
EXPECTED_TOKEN = "GPT54_OK"


def _powershell_quote(arg: str) -> str:
    return "'" + arg.replace("'", "''") + "'"


def _looks_like_command_not_found(output: str, command_name: str) -> bool:
    lowered = output.lower()
    return (
        f"{command_name.lower()}: command not found" in lowered
        or f"'{command_name.lower()}' is not recognized" in lowered
        or f"{command_name.lower()} is not recognized" in lowered
    )


def _default_command_runner(args: list[str]) -> subprocess.CompletedProcess[str]:
    if os.name == "nt":
        command = (
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
            "$OutputEncoding = [System.Text.Encoding]::UTF8; "
            "& " + " ".join(_powershell_quote(arg) for arg in args)
        )
        return subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)


def run_codex_healthcheck(command_runner: CommandRunner | None = None) -> dict[str, Any]:
    runner = command_runner or _default_command_runner

    try:
        codex_version_result = runner(["codex", "--version"])
    except FileNotFoundError:
        return {
            "ok": False,
            "stage": "codex-missing",
            "message": "Codex CLI is not available on PATH.",
        }

    codex_version_output = f"{codex_version_result.stdout}\n{codex_version_result.stderr}".strip()
    if _looks_like_command_not_found(codex_version_output, "codex"):
        return {
            "ok": False,
            "stage": "codex-missing",
            "message": "Codex CLI is not available on PATH.",
            "detail": codex_version_output,
        }
    if codex_version_result.returncode != 0:
        return {
            "ok": False,
            "stage": "codex-cli-failed",
            "message": "Codex CLI responded, but the basic invocation failed.",
            "detail": codex_version_output,
        }

    try:
        codex_result = runner(["codex", "exec", "-m", "gpt-5.4", f"Reply with exactly: {EXPECTED_TOKEN}"])
    except FileNotFoundError:
        return {
            "ok": False,
            "stage": "codex-missing",
            "message": "Codex CLI is not available on PATH.",
        }

    codex_output = f"{codex_result.stdout}\n{codex_result.stderr}".strip()
    if _looks_like_command_not_found(codex_output, "codex"):
        return {
            "ok": False,
            "stage": "codex-missing",
            "message": "Codex CLI is not available on PATH.",
            "detail": codex_output,
        }
    if codex_result.returncode != 0:
        return {
            "ok": False,
            "stage": "gpt-call-failed",
            "message": "Codex reached execution but GPT-5.4 healthcheck failed.",
            "detail": codex_output,
        }

    if EXPECTED_TOKEN not in codex_output:
        return {
            "ok": False,
            "stage": "gpt-token-mismatch",
            "message": "Codex executed, but GPT-5.4 did not return the expected healthcheck token.",
            "detail": codex_output,
        }

    return {
        "ok": True,
        "stage": "ok",
        "message": "Codex reached GPT-5.4 and returned GPT54_OK.",
        "detail": codex_version_output,
    }
