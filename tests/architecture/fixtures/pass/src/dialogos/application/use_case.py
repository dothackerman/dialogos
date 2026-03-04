from __future__ import annotations

from dialogos.domain.model import Turn
from dialogos.ports.sender import Sender


def send_turn(turn: Turn, sender: Sender) -> None:
    sender.send(turn.text)
