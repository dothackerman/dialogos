from __future__ import annotations

import subprocess

import pytest

from silicato.adapters.tmux.runtime import TmuxRuntime


def test_tmux_runtime_contract_list_panes_builds_expected_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        _ = kwargs
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    runtime = TmuxRuntime()
    _ = runtime.list_panes(all_panes=True, pane_format="#{pane_id}")
    _ = runtime.list_panes(target="codex:0.1")

    assert calls == [
        ["tmux", "list-panes", "-a", "-F", "#{pane_id}"],
        ["tmux", "list-panes", "-t", "codex:0.1"],
    ]


def test_tmux_runtime_contract_common_commands_build_expected_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        _ = kwargs
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    runtime = TmuxRuntime()
    _ = runtime.new_session("s1", command="cat")
    _ = runtime.send_keys("s1:0.0", "hello", "C-m")
    _ = runtime.capture_pane("s1:0.0")
    _ = runtime.kill_session("s1")

    assert calls == [
        ["tmux", "new-session", "-d", "-s", "s1", "cat"],
        ["tmux", "send-keys", "-t", "s1:0.0", "hello", "C-m"],
        ["tmux", "capture-pane", "-pt", "s1:0.0"],
        ["tmux", "kill-session", "-t", "s1"],
    ]
