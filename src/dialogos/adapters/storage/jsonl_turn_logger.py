"""JSONL turn logging adapter."""

from __future__ import annotations

from pathlib import Path

from dialogos.logging_jsonl import TurnLogEvent as LegacyTurnLogEvent
from dialogos.logging_jsonl import append_turn_log
from dialogos.ports.storage import TurnLogEvent, TurnLoggerPort


class JsonlTurnLogger(TurnLoggerPort):
    """Adapter for structured JSONL turn logging."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path

    def append(self, event: TurnLogEvent) -> Path:
        return append_turn_log(
            LegacyTurnLogEvent(
                action=event.action,
                transcript=event.transcript,
                language=event.language,
                tmux_target=event.tmux_target,
                preview=event.preview,
                sent=event.sent,
            ),
            path=self._path,
        )
