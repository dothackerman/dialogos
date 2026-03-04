"""Use case for tmux target resolution policy."""

from __future__ import annotations

from dataclasses import dataclass

from dialogos.ports.targeting import (
    InvalidTmuxTargetError,
    NoTmuxSessionError,
    PickerAbortedError,
    TargetResolverPort,
)


@dataclass(frozen=True)
class ResolveTargetResult:
    target: str
    remembered_target_error: str | None = None


class ResolveTargetUseCase:
    """Resolves tmux target following CLI/env/config/picker precedence."""

    def __init__(self, resolver: TargetResolverPort) -> None:
        self._resolver = resolver

    def execute(
        self,
        *,
        explicit_target: str | None,
        pick_target: bool,
        env_target: str | None,
        remembered_target: str | None,
    ) -> ResolveTargetResult:
        if isinstance(explicit_target, str) and explicit_target:
            self._resolver.validate_target(explicit_target)
            return ResolveTargetResult(target=explicit_target)

        if not pick_target and env_target:
            self._resolver.validate_target(env_target)
            return ResolveTargetResult(target=env_target)

        if not pick_target and remembered_target:
            try:
                self._resolver.validate_target(remembered_target)
                return ResolveTargetResult(target=remembered_target)
            except InvalidTmuxTargetError as exc:
                panes = self._resolver.list_panes()
                picked = self._resolver.pick_target_interactive(panes)
                return ResolveTargetResult(target=picked, remembered_target_error=str(exc))
            except (NoTmuxSessionError, PickerAbortedError):
                raise

        panes = self._resolver.list_panes()
        picked = self._resolver.pick_target_interactive(panes)
        return ResolveTargetResult(target=picked)
