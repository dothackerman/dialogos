from __future__ import annotations

from silicato.adapters.tmux.sender import TmuxSender


def build_sender() -> TmuxSender:
    return TmuxSender()
