from __future__ import annotations

import subprocess

import pytest

from dialogos.adapters.tmux.sender import TmuxSender


def test_tmux_sender_contract_sends_message(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(cmd)
        _ = kwargs
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    sender = TmuxSender("codex:0.1")
    sender.send("hello")

    assert calls == [["tmux", "send-keys", "-t", "codex:0.1", "hello", "C-m"]]


def test_tmux_sender_contract_raises_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        _ = kwargs
        return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="", stderr="tmux error")

    monkeypatch.setattr(subprocess, "run", fake_run)

    sender = TmuxSender("codex:0.1")
    with pytest.raises(RuntimeError, match="tmux error"):
        sender.send("hello")
