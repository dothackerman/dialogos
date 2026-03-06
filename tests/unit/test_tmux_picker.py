from __future__ import annotations

import subprocess
from collections.abc import Iterator
from contextlib import contextmanager

import pytest

from silicato.adapters.tmux.target_resolver import TmuxTargetResolver
from silicato.ports.targeting import (
    InvalidTmuxTargetError,
    NoTmuxSessionError,
    PaneEntry,
    PickerAbortedError,
)


@contextmanager
def patched_run(
    monkeypatch: pytest.MonkeyPatch, result: subprocess.CompletedProcess[str]
) -> Iterator[None]:
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: result)
    yield


def test_list_panes_parses_tmux_output(monkeypatch: pytest.MonkeyPatch) -> None:
    result = subprocess.CompletedProcess(
        args=["tmux"],
        returncode=0,
        stdout="codex:0.1\tbash\tmain\nwork:2.0\tpython\tworker\n",
        stderr="",
    )
    with patched_run(monkeypatch, result):
        panes = TmuxTargetResolver().list_panes()

    assert panes == [
        PaneEntry(target="codex:0.1", command="bash", title="main"),
        PaneEntry(target="work:2.0", command="python", title="worker"),
    ]


def test_list_panes_raises_when_no_tmux_session(monkeypatch: pytest.MonkeyPatch) -> None:
    result = subprocess.CompletedProcess(
        args=["tmux"],
        returncode=1,
        stdout="",
        stderr="failed to connect to server",
    )
    with patched_run(monkeypatch, result):
        with pytest.raises(NoTmuxSessionError):
            _ = TmuxTargetResolver().list_panes()


def test_validate_target_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    result = subprocess.CompletedProcess(
        args=["tmux"],
        returncode=1,
        stdout="",
        stderr="can't find pane",
    )
    with patched_run(monkeypatch, result):
        with pytest.raises(InvalidTmuxTargetError):
            TmuxTargetResolver().validate_target("bad:0.1")


def test_validate_target_accepts_pane_scoped_target(monkeypatch: pytest.MonkeyPatch) -> None:
    result = subprocess.CompletedProcess(
        args=["tmux"],
        returncode=0,
        stdout="codex:0.1\tbash\tmain\n",
        stderr="",
    )
    with patched_run(monkeypatch, result):
        TmuxTargetResolver().validate_target("codex:0.1")


def test_validate_target_rejects_window_scoped_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = subprocess.CompletedProcess(
        args=["tmux"],
        returncode=0,
        stdout="codex:0.0\tbash\tmain\ncodex:0.1\tpython\tworker\n",
        stderr="",
    )
    with patched_run(monkeypatch, result):
        with pytest.raises(InvalidTmuxTargetError, match="pane-scoped"):
            TmuxTargetResolver().validate_target("codex:0")


def test_pick_target_interactive_by_index() -> None:
    panes = [
        PaneEntry(target="codex:0.1", command="bash", title="main"),
        PaneEntry(target="work:1.0", command="python", title="worker"),
    ]
    answers = iter(["2"])
    printed: list[str] = []

    target = TmuxTargetResolver().pick_target_interactive(
        panes,
        input_fn=lambda _: next(answers),
        print_fn=printed.append,
    )

    assert target == "work:1.0"
    assert any("[1]" in line for line in printed)


def test_pick_target_interactive_abort() -> None:
    panes = [PaneEntry(target="codex:0.1", command="bash", title="main")]

    with pytest.raises(PickerAbortedError):
        _ = TmuxTargetResolver().pick_target_interactive(
            panes,
            input_fn=lambda _: "q",
            print_fn=lambda _: None,
        )


def test_print_no_tmux_guidance_outputs_expected_steps() -> None:
    lines: list[str] = []

    TmuxTargetResolver().print_no_tmux_guidance(print_fn=lines.append)

    assert lines == [
        "No tmux session is running.",
        "Start one with:",
        "  tmux new -s agent",
        "Then start your agent CLI (for example Codex or Claude Code) and rerun Silicato.",
    ]
