"""Core contracts used to keep module boundaries explicit."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class TranscriptResult:
    text: str
    language: str


class AudioCapture(Protocol):
    def record_once(
        self, output_path: Path, sample_rate: int, input_device: str | None
    ) -> None: ...


class SpeechToText(Protocol):
    def transcribe(self, wav_path: Path, language: str) -> TranscriptResult: ...


class Sender(Protocol):
    def send(self, text: str) -> None: ...
