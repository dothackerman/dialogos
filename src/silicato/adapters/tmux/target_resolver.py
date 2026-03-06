"""tmux target resolver adapter."""

from __future__ import annotations

import subprocess
from collections.abc import Callable

from silicato.ports.targeting import (
    InvalidTmuxTargetError,
    NoTmuxSessionError,
    PaneEntry,
    PickerAbortedError,
    TargetResolverPort,
)

TMUX_PANE_FORMAT = (
    "#{session_name}:#{window_index}.#{pane_index}\t#{pane_current_command}\t#{pane_title}"
)


def _detect_no_session(text: str) -> bool:
    lowered = text.lower()
    return "no server running" in lowered or "failed to connect" in lowered


class TmuxTargetResolver(TargetResolverPort):
    """Adapter for validating and selecting tmux targets."""

    def validate_target(self, target: str) -> None:
        result = subprocess.run(
            ["tmux", "list-panes", "-t", target],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return
        message = (result.stderr or result.stdout or "invalid tmux target").strip()
        if _detect_no_session(message):
            raise NoTmuxSessionError(message)
        raise InvalidTmuxTargetError(message)

    def list_panes(self) -> list[PaneEntry]:
        result = subprocess.run(
            ["tmux", "list-panes", "-a", "-F", TMUX_PANE_FORMAT],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            message = (result.stderr or result.stdout or "tmux list-panes failed").strip()
            if _detect_no_session(message):
                raise NoTmuxSessionError(message)
            raise RuntimeError(message)

        panes: list[PaneEntry] = []
        for raw in (result.stdout or "").splitlines():
            if not raw.strip():
                continue
            parts = raw.split("\t")
            if len(parts) < 3:
                continue
            panes.append(PaneEntry(target=parts[0], command=parts[1], title=parts[2]))
        return panes

    def pick_target_interactive(
        self,
        panes: list[PaneEntry],
        *,
        input_fn: Callable[[str], str] = input,
        print_fn: Callable[[str], None] = print,
    ) -> str:
        if not panes:
            raise NoTmuxSessionError("No tmux panes found.")

        print_fn("Available tmux panes:")
        for index, pane in enumerate(panes, start=1):
            title = pane.title or "-"
            command = pane.command or "-"
            print_fn(f"  [{index}] {pane.target} | cmd={command} | title={title}")

        while True:
            raw = input_fn("Select target pane by number (or q to quit): ").strip().lower()
            if raw in {"q", "quit", "exit"}:
                raise PickerAbortedError("Target selection aborted by user.")
            if raw.isdigit():
                selected = int(raw)
                if 1 <= selected <= len(panes):
                    return panes[selected - 1].target
            print_fn(f"Invalid selection '{raw}'. Enter a number between 1 and {len(panes)}.")

    def print_no_tmux_guidance(self, *, print_fn: Callable[[str], None] = print) -> None:
        print_fn("No tmux session is running.")
        print_fn("Start one with:")
        print_fn("  tmux new -s agent")
        print_fn("Then start your agent CLI (for example Codex or Claude Code) and rerun Silicato.")
