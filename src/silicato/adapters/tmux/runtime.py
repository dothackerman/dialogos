"""tmux runtime command boundary."""

from __future__ import annotations

import subprocess


class TmuxRuntime:
    """Single boundary for tmux command execution."""

    def _run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["tmux", *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def send_keys(self, target: str, *keys: str) -> subprocess.CompletedProcess[str]:
        return self._run(["send-keys", "-t", target, *keys])

    def list_panes(
        self,
        *,
        target: str | None = None,
        all_panes: bool = False,
        pane_format: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        args = ["list-panes"]
        if all_panes:
            args.append("-a")
        if target is not None:
            args.extend(["-t", target])
        if pane_format is not None:
            args.extend(["-F", pane_format])
        return self._run(args)

    def new_session(
        self,
        session_name: str,
        *,
        detached: bool = True,
        command: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        args = ["new-session"]
        if detached:
            args.append("-d")
        args.extend(["-s", session_name])
        if command is not None:
            args.append(command)
        return self._run(args)

    def capture_pane(self, target: str) -> subprocess.CompletedProcess[str]:
        return self._run(["capture-pane", "-pt", target])

    def kill_session(self, session_name: str) -> subprocess.CompletedProcess[str]:
        return self._run(["kill-session", "-t", session_name])
