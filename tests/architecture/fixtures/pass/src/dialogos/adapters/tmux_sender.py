from __future__ import annotations

from dialogos.ports.sender import Sender


class TmuxSender(Sender):
    def send(self, text: str) -> None:
        _ = text
