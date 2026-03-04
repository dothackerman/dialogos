"""Use case for capture + transcribe execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dialogos.domain.turn_state import normalize_transcript
from dialogos.ports.audio import AudioCapturePort
from dialogos.ports.stt import SpeechToTextPort, TranscriptResult


@dataclass(frozen=True)
class TurnConfig:
    sample_rate: int = 16000
    input_device: str | None = None
    language: str = "auto"


class RunCaptureTranscribeUseCase:
    """Orchestrates one capture/transcribe pass."""

    def __init__(self, capture: AudioCapturePort, stt: SpeechToTextPort) -> None:
        self._capture = capture
        self._stt = stt

    def execute(self, wav_path: Path, config: TurnConfig) -> TranscriptResult:
        self._capture.record_once(wav_path, config.sample_rate, config.input_device)
        result = self._stt.transcribe(wav_path, config.language)
        return TranscriptResult(text=normalize_transcript(result.text), language=result.language)
