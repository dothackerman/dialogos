"""tmux sender adapter placeholder for MVP Codex transport."""

from __future__ import annotations

import subprocess

from dialogos.contracts import Sender


class TmuxSender(Sender):
    """Send text to a tmux target pane by simulating Enter."""

    def __init__(self, target: str) -> None:
        self.target = target

    def send(self, text: str) -> None:
        subprocess.run(
            ["tmux", "send-keys", "-t", self.target, text, "C-m"],
            check=True,
        )
