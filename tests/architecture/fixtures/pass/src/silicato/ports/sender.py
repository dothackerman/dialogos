from __future__ import annotations

from typing import Protocol


class Sender(Protocol):
    def send(self, text: str) -> None: ...
