from __future__ import annotations

import json
from pathlib import Path

from dialogos.adapters.storage.jsonl_turn_logger import JsonlTurnLogger
from dialogos.ports.storage import TurnLogEvent


def test_turn_logger_contract_appends_jsonl_events(tmp_path: Path) -> None:
    log_path = tmp_path / "turns.jsonl"
    logger = JsonlTurnLogger(path=log_path)

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

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    second = json.loads(lines[1])

    assert first["action"] == "send"
    assert first["sent"] is True
    assert second["action"] == "skip"
    assert second["preview"] is True
