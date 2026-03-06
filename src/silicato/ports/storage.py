"""Persistence ports for config and turn logs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class SilicatoConfig:
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

    def load(self) -> SilicatoConfig: ...

    def save(self, config: SilicatoConfig) -> Path: ...


class TurnLoggerPort(Protocol):
    """Capability for appending structured turn events."""

    def append(self, event: TurnLogEvent) -> Path: ...
