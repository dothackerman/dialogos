"""Pure confirm-action parsing logic."""

from __future__ import annotations

from typing import Literal

ConfirmAction = Literal["send", "edit", "retry", "skip", "quit"]


def parse_confirm_action(raw: str, *, preview_mode: bool) -> ConfirmAction | None:
    """Parse one confirm prompt choice into an action."""

    choice = raw.strip().lower()
    if preview_mode:
        if choice in {"y", "yes", "send"}:
            return "send"
        if choice in {"e", "edit"}:
            return "edit"
        if choice in {"r", "retry"}:
            return "retry"
        if choice in {"s", "skip"}:
            return "skip"
        if choice in {"q", "quit", "exit"}:
            return "quit"
        return None

    if choice in {"", "y", "yes", "send"}:
        return "send"
    if choice in {"e", "edit"}:
        return "edit"
    if choice in {"r", "retry"}:
        return "retry"
    if choice in {"s", "skip"}:
        return "skip"
    if choice in {"q", "quit", "exit"}:
        return "quit"
    return None
