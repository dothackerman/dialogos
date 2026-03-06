from __future__ import annotations

from silicato.domain.model import Turn
from silicato.ports.sender import Sender


def send_turn(turn: Turn, sender: Sender) -> None:
    sender.send(turn.text)
