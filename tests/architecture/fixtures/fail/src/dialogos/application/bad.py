from __future__ import annotations

from dialogos.adapters.tmux.sender import TmuxSender


def build_sender() -> TmuxSender:
    return TmuxSender()
