from __future__ import annotations

import pytest

from dialogos.adapters.tmux.target_resolver import TmuxTargetResolver
from dialogos.ports.targeting import (
    InvalidTmuxTargetError,
    NoTmuxSessionError,
    PaneEntry,
    PickerAbortedError,
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


def test_target_resolver_contract_returns_panes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "dialogos.adapters.tmux.target_resolver.list_panes",
        lambda: [LegacyPaneEntry(target="codex:0.1", command="bash", title="main")],
    )

    resolver = TmuxTargetResolver()
    panes = resolver.list_panes()

    assert panes == [PaneEntry(target="codex:0.1", command="bash", title="main")]


def test_target_resolver_contract_maps_validation_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_validate(target: str) -> None:
        _ = target
        raise LegacyInvalidTmuxTargetError("bad")

    monkeypatch.setattr("dialogos.adapters.tmux.target_resolver.validate_target", fail_validate)

    resolver = TmuxTargetResolver()
    with pytest.raises(InvalidTmuxTargetError, match="bad"):
        resolver.validate_target("bad:0.1")


def test_target_resolver_contract_maps_no_session_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_validate(target: str) -> None:
        _ = target
        raise LegacyNoTmuxSessionError("no server")

    monkeypatch.setattr("dialogos.adapters.tmux.target_resolver.validate_target", fail_validate)

    resolver = TmuxTargetResolver()
    with pytest.raises(NoTmuxSessionError, match="no server"):
        resolver.validate_target("codex:0.1")


def test_target_resolver_contract_maps_picker_abort(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_pick(*args: object, **kwargs: object) -> str:
        _ = args
        _ = kwargs
        raise LegacyPickerAbortedError("aborted")

    monkeypatch.setattr(
        "dialogos.adapters.tmux.target_resolver.pick_target_interactive",
        fail_pick,
    )

    resolver = TmuxTargetResolver()
    with pytest.raises(PickerAbortedError, match="aborted"):
        resolver.pick_target_interactive(
            [PaneEntry(target="codex:0.1", command="bash", title="main")]
        )
