"""Text sender port."""

from __future__ import annotations

from typing import Protocol


class SenderPort(Protocol):
    """Capability for delivering text to a target."""

    def send(self, text: str) -> None: ...
