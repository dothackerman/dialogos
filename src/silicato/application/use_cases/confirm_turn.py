"""Use case for confirm-action parsing."""

from __future__ import annotations

from silicato.domain.confirm_actions import ConfirmAction, parse_confirm_action


class ConfirmTurnUseCase:
    """Parses and validates confirm menu choices."""

    def execute(self, raw_choice: str, *, preview_mode: bool) -> ConfirmAction | None:
        return parse_confirm_action(raw_choice, preview_mode=preview_mode)
