"""tmux target resolver adapter."""

from __future__ import annotations

from collections.abc import Callable

from dialogos.ports.targeting import (
    InvalidTmuxTargetError,
    NoTmuxSessionError,
    PaneEntry,
    PickerAbortedError,
    TargetResolverPort,
)
from dialogos.tmux_picker import (
    InvalidTmuxTargetError as LegacyInvalidTmuxTargetError,
)
from dialogos.tmux_picker import (
    NoTmuxSessionError as LegacyNoTmuxSessionError,
)
from dialogos.tmux_picker import (
    PaneEntry as LegacyPaneEntry,
)
from dialogos.tmux_picker import (
    PickerAbortedError as LegacyPickerAbortedError,
)
from dialogos.tmux_picker import (
    list_panes,
    pick_target_interactive,
    print_no_tmux_guidance,
    validate_target,
)


class TmuxTargetResolver(TargetResolverPort):
    """Adapter that proxies tmux targeting through existing tmux integration."""

    def validate_target(self, target: str) -> None:
        try:
            validate_target(target)
        except LegacyNoTmuxSessionError as exc:
            raise NoTmuxSessionError(str(exc)) from exc
        except LegacyInvalidTmuxTargetError as exc:
            raise InvalidTmuxTargetError(str(exc)) from exc

    def list_panes(self) -> list[PaneEntry]:
        try:
            panes = list_panes()
        except LegacyNoTmuxSessionError as exc:
            raise NoTmuxSessionError(str(exc)) from exc
        return [PaneEntry(target=p.target, command=p.command, title=p.title) for p in panes]

    def pick_target_interactive(
        self,
        panes: list[PaneEntry],
        *,
        input_fn: Callable[[str], str] = input,
        print_fn: Callable[[str], None] = print,
    ) -> str:
        legacy_panes = [
            LegacyPaneEntry(target=p.target, command=p.command, title=p.title) for p in panes
        ]
        try:
            return pick_target_interactive(legacy_panes, input_fn=input_fn, print_fn=print_fn)
        except LegacyNoTmuxSessionError as exc:
            raise NoTmuxSessionError(str(exc)) from exc
        except LegacyPickerAbortedError as exc:
            raise PickerAbortedError(str(exc)) from exc

    def print_no_tmux_guidance(self, *, print_fn: Callable[[str], None] = print) -> None:
        print_no_tmux_guidance(print_fn=print_fn)
