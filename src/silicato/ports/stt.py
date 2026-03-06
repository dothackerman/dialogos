"""Speech-to-text port."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class TranscriptResult:
    text: str
    language: str


class SpeechToTextPort(Protocol):
    """Capability for transcribing an audio file."""

    def transcribe(self, wav_path: Path, language: str) -> TranscriptResult: ...
