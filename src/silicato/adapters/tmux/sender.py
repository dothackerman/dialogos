"""tmux sender adapter."""

from __future__ import annotations

import time

from silicato.ports.sender import SenderPort

from .runtime import TmuxRuntime


class TmuxSender(SenderPort):
    """Send text to a tmux target pane and submit it."""

    # Some agent TUIs can miss submit when text + Enter are sent in one tmux call.
    # A short split delay makes submission reliable in practice.
    SUBMIT_DELAY_SECONDS = 0.05

    def __init__(self, target: str, *, runtime: TmuxRuntime | None = None) -> None:
        self.target = target
        self._runtime = runtime or TmuxRuntime()

    def send(self, text: str) -> None:
        text_result = self._runtime.send_keys(self.target, text)
        if text_result.returncode != 0:
            message = (text_result.stderr or text_result.stdout or "tmux send-keys failed").strip()
            raise RuntimeError(message)

        time.sleep(self.SUBMIT_DELAY_SECONDS)

        submit_result = self._runtime.send_keys(self.target, "Enter")
        if submit_result.returncode != 0:
            message = (
                submit_result.stderr or submit_result.stdout or "tmux submit-key send failed"
            ).strip()
            raise RuntimeError(message)
