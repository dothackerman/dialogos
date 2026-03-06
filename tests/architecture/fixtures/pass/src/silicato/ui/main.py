from __future__ import annotations

from silicato.adapters.tmux.sender import TmuxSender
from silicato.application.use_case import send_turn


class CliWiring:
    sender_cls = TmuxSender
    run = staticmethod(send_turn)
