"""Use case for turn logging."""

from __future__ import annotations

from dialogos.ports.storage import TurnLogEvent, TurnLoggerPort


class LogTurnUseCase:
    """Appends structured turn log events."""

    def __init__(self, logger: TurnLoggerPort) -> None:
        self._logger = logger

    def execute(
        self,
        *,
        action: str,
        transcript: str,
        language: str,
        tmux_target: str,
        preview: bool,
        sent: bool,
    ) -> None:
        self._logger.append(
            TurnLogEvent(
                action=action,
                transcript=transcript,
                language=language,
                tmux_target=tmux_target,
                preview=preview,
                sent=sent,
            )
        )
