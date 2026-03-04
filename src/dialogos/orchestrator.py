"""Orchestration and confirmation helpers for Dialogos turns."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .contracts import AudioCapture, Sender, SpeechToText, TranscriptResult

ConfirmAction = Literal["send", "edit", "retry", "skip", "quit"]


@dataclass
class TurnConfig:
    sample_rate: int = 16000
    input_device: str | None = None
    language: str = "auto"


@dataclass(frozen=True)
class TurnAction:
    """Represents one decision from the confirm menu."""

    action: ConfirmAction
    transcript: str


class PushToTalkOrchestrator:
    """Single-turn orchestration for capture -> transcribe -> optional send."""

    def __init__(
        self, capture: AudioCapture, stt: SpeechToText, sender: Sender | None = None
    ) -> None:
        self.capture = capture
        self.stt = stt
        self.sender = sender

    def run_turn(self, wav_path: Path, config: TurnConfig, *, send_text: bool) -> TranscriptResult:
        self.capture.record_once(wav_path, config.sample_rate, config.input_device)
        transcript = self.stt.transcribe(wav_path, config.language)
        if send_text and self.sender is not None and transcript.text:
            self.sender.send(transcript.text)
        return transcript


def parse_confirm_action(raw: str, *, preview_mode: bool) -> ConfirmAction | None:
    """Parse a confirm prompt choice into an action.

    Normal mode allows empty input as implicit send.
    Preview mode requires explicit send (`y`/`send`).
    """

    choice = raw.strip().lower()
    if preview_mode:
        if choice in {"y", "yes", "send"}:
            return "send"
        if choice in {"e", "edit"}:
            return "edit"
        if choice in {"r", "retry"}:
            return "retry"
        if choice in {"s", "skip"}:
            return "skip"
        if choice in {"q", "quit", "exit"}:
            return "quit"
        return None

    if choice in {"", "y", "yes", "send"}:
        return "send"
    if choice in {"e", "edit"}:
        return "edit"
    if choice in {"r", "retry"}:
        return "retry"
    if choice in {"s", "skip"}:
        return "skip"
    if choice in {"q", "quit", "exit"}:
        return "quit"
    return None
