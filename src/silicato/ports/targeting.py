"""Target resolution port for tmux pane workflows."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol


class TargetingError(RuntimeError):
    """Base class for target resolution failures."""


class NoTmuxSessionError(TargetingError):
    """Raised when no tmux server/session is available."""


class InvalidTmuxTargetError(TargetingError):
    """Raised when a target pane cannot be resolved."""


class PickerAbortedError(TargetingError):
    """Raised when user aborts target selection."""


@dataclass(frozen=True)
class PaneEntry:
    target: str
    command: str
    title: str


class TargetResolverPort(Protocol):
    """Capability for validating and selecting tmux targets."""

    def validate_target(self, target: str) -> None: ...

    def list_panes(self) -> list[PaneEntry]: ...

    def pick_target_interactive(
        self,
        panes: list[PaneEntry],
        *,
        input_fn: Callable[[str], str] = input,
        print_fn: Callable[[str], None] = print,
    ) -> str: ...

    def print_no_tmux_guidance(self, *, print_fn: Callable[[str], None] = print) -> None: ...
