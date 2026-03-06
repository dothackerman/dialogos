from __future__ import annotations

import subprocess

import pytest

from silicato.adapters.tmux.target_resolver import TmuxTargetResolver
from silicato.ports.targeting import (
    InvalidTmuxTargetError,
    NoTmuxSessionError,
    PaneEntry,
    PickerAbortedError,
)


def test_target_resolver_contract_returns_panes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=["tmux"],
            returncode=0,
            stdout="codex:0.1\tbash\tmain\n",
            stderr="",
        ),
    )

    resolver = TmuxTargetResolver()
    panes = resolver.list_panes()

    assert panes == [PaneEntry(target="codex:0.1", command="bash", title="main")]


def test_target_resolver_contract_maps_validation_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=["tmux"],
            returncode=1,
            stdout="",
            stderr="can't find pane",
        ),
    )

    resolver = TmuxTargetResolver()
    with pytest.raises(InvalidTmuxTargetError, match="can't find pane"):
        resolver.validate_target("bad:0.1")


def test_target_resolver_contract_maps_no_session_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=["tmux"],
            returncode=1,
            stdout="",
            stderr="failed to connect to server",
        ),
    )

    resolver = TmuxTargetResolver()
    with pytest.raises(NoTmuxSessionError, match="failed to connect to server"):
        resolver.validate_target("codex:0.1")


def test_target_resolver_contract_maps_picker_abort() -> None:
    resolver = TmuxTargetResolver()
    with pytest.raises(PickerAbortedError, match="Target selection aborted"):
        resolver.pick_target_interactive(
            [PaneEntry(target="codex:0.1", command="bash", title="main")],
            input_fn=lambda _: "q",
            print_fn=lambda _: None,
        )
