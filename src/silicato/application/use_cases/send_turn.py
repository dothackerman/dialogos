"""Use case for sending a transcript."""

from __future__ import annotations

from silicato.ports.sender import SenderPort


class SendTurnUseCase:
    """Sends text via configured sender port."""

    def __init__(self, sender: SenderPort) -> None:
        self._sender = sender

    def execute(self, text: str) -> None:
        self._sender.send(text)
