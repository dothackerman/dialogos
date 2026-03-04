"""Orchestration layer for voice input flows.

The current CLI is still function-based for speed of iteration, but this module
defines the intended direction: adapters plus explicit orchestration.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .contracts import AudioCapture, Sender, SpeechToText, TranscriptResult


@dataclass
class TurnConfig:
    sample_rate: int = 16000
    input_device: str | None = None
    language: str = "auto"


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
