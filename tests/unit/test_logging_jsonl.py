from __future__ import annotations

import json
from pathlib import Path

import pytest

from dialogos.adapters.storage.jsonl_turn_logger import JsonlTurnLogger, default_log_path
from dialogos.ports.storage import TurnLogEvent


def test_default_log_path_uses_xdg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", "/tmp/xdg-state")
    assert default_log_path() == Path("/tmp/xdg-state/dialogos/turns.jsonl")


def test_append_turn_log_writes_schema_and_appends(tmp_path: Path) -> None:
    log_file = tmp_path / "turns.jsonl"
    logger = JsonlTurnLogger(path=log_file)

    logger.append(
        TurnLogEvent(
            action="send",
            transcript="hello",
            language="en",
            tmux_target="codex:0.1",
            preview=False,
            sent=True,
        )
    )
    logger.append(
        TurnLogEvent(
            action="skip",
            transcript="",
            language="auto",
            tmux_target="codex:0.1",
            preview=True,
            sent=False,
        )
    )

    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2

    first = json.loads(lines[0])
    second = json.loads(lines[1])

    for entry in (first, second):
        assert set(entry.keys()) == {
            "timestamp",
            "action",
            "transcript",
            "language",
            "tmux_target",
            "preview",
            "sent",
        }

    assert first["action"] == "send"
    assert first["sent"] is True
    assert second["action"] == "skip"
    assert second["preview"] is True
