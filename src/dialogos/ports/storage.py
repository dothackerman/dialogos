"""Persistence ports for config and turn logs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class DialogosConfig:
    tmux_target: str | None = None


@dataclass(frozen=True)
class TurnLogEvent:
    action: str
    transcript: str
    language: str
    tmux_target: str | None
    preview: bool
    sent: bool


class ConfigStorePort(Protocol):
    """Capability for loading/saving user configuration."""

    def load(self) -> DialogosConfig: ...

    def save(self, config: DialogosConfig) -> Path: ...


class TurnLoggerPort(Protocol):
    """Capability for appending structured turn events."""

    def append(self, event: TurnLogEvent) -> Path: ...
