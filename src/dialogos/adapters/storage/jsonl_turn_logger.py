"""JSONL turn logging adapter."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

from dialogos.ports.storage import TurnLogEvent, TurnLoggerPort


def default_log_path() -> Path:
    """Resolve the default JSONL log path using XDG conventions."""

    xdg_root = os.environ.get("XDG_STATE_HOME")
    if xdg_root:
        return Path(xdg_root) / "dialogos" / "turns.jsonl"
    return Path.home() / ".local" / "state" / "dialogos" / "turns.jsonl"


class JsonlTurnLogger(TurnLoggerPort):
    """Adapter for structured JSONL turn logging."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path

    def append(self, event: TurnLogEvent) -> Path:
        log_path = self._path or default_log_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "action": event.action,
            "transcript": event.transcript,
            "language": event.language,
            "tmux_target": event.tmux_target,
            "preview": event.preview,
            "sent": event.sent,
        }

        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")
        return log_path
