from __future__ import annotations

from argparse import Namespace

import pytest

import dialogos.cli as cli
from dialogos.tmux_picker import InvalidTmuxTargetError


def test_is_cuda_runtime_missing_true() -> None:
    err = RuntimeError("Library libcublas.so.12 is not found or cannot be loaded")
    assert cli.is_cuda_runtime_missing(err)


def test_is_cuda_runtime_missing_false() -> None:
    err = RuntimeError("some unrelated runtime error")
    assert not cli.is_cuda_runtime_missing(err)


def test_resolve_tmux_target_prefers_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    validated: list[str] = []

    def fake_validate(target: str) -> None:
        validated.append(target)

    monkeypatch.setattr(cli, "validate_target", fake_validate)
    monkeypatch.setattr(cli, "list_panes", lambda: [])
    monkeypatch.setattr(cli, "pick_target_interactive", lambda panes: "ignored")

    args = Namespace(tmux_target="cli:0.1", pick_target=False)
    target = cli.resolve_tmux_target(args, remembered_target="cfg:0.1")

    assert target == "cli:0.1"
    assert validated == ["cli:0.1"]


def test_resolve_tmux_target_falls_back_to_picker_for_invalid_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_validate(target: str) -> None:
        if target == "bad:target":
            raise InvalidTmuxTargetError("bad")

    monkeypatch.setattr(cli, "validate_target", fake_validate)
    monkeypatch.setattr(cli, "list_panes", lambda: [object()])
    monkeypatch.setattr(cli, "pick_target_interactive", lambda panes: "picked:0.1")

    args = Namespace(tmux_target=None, pick_target=False)
    target = cli.resolve_tmux_target(args, remembered_target="bad:target")

    assert target == "picked:0.1"


def test_resolve_tmux_target_uses_env_when_available(monkeypatch: pytest.MonkeyPatch) -> None:
    validated: list[str] = []

    def fake_validate(target: str) -> None:
        validated.append(target)

    monkeypatch.setattr(cli, "validate_target", fake_validate)
    monkeypatch.setenv("DIALOGOS_TMUX_TARGET", "env:0.5")
    args = Namespace(tmux_target=None, pick_target=False)

    target = cli.resolve_tmux_target(args, remembered_target=None)

    assert target == "env:0.5"
    assert validated == ["env:0.5"]
