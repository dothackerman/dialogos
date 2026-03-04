"""JSONL turn logging for local debugging and traceability."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class TurnLogEvent:
    """Schema for one turn entry in the JSONL log."""

    action: str
    transcript: str
    language: str
    tmux_target: str | None
    preview: bool
    sent: bool


def default_log_path() -> Path:
    """Resolve the default JSONL log path using XDG conventions."""

    xdg_root = os.environ.get("XDG_STATE_HOME")
    if xdg_root:
        return Path(xdg_root) / "dialogos" / "turns.jsonl"
    return Path.home() / ".local" / "state" / "dialogos" / "turns.jsonl"


def append_turn_log(event: TurnLogEvent, path: Path | None = None) -> Path:
    """Append one structured event to the local JSONL log file."""

    log_path = path or default_log_path()
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
