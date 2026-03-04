from __future__ import annotations

from dialogos.adapters.tmux.sender import TmuxSender
from dialogos.application.use_case import send_turn


class CliWiring:
    sender_cls = TmuxSender
    run = staticmethod(send_turn)
