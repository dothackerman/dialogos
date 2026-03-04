"""tmux sender adapter."""

from __future__ import annotations

import subprocess

from dialogos.ports.sender import SenderPort


class TmuxSender(SenderPort):
    """Send text to a tmux target pane by simulating Enter."""

    def __init__(self, target: str) -> None:
        self.target = target

    def send(self, text: str) -> None:
        result = subprocess.run(
            ["tmux", "send-keys", "-t", self.target, text, "C-m"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            message = (result.stderr or result.stdout or "tmux send-keys failed").strip()
            raise RuntimeError(message)
