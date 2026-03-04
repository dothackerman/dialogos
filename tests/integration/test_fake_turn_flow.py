from __future__ import annotations

from pathlib import Path

from dialogos.contracts import TranscriptResult
from dialogos.orchestrator import PushToTalkOrchestrator, TurnConfig


class CaptureAdapter:
    def record_once(self, output_path: Path, sample_rate: int, input_device: str | None) -> None:
        output_path.write_bytes(b"RIFF....WAVE")
        _ = sample_rate
        _ = input_device


class SttAdapter:
    def transcribe(self, wav_path: Path, language: str) -> TranscriptResult:
        _ = wav_path
        return TranscriptResult(text="integration transcript", language=language)


class SenderAdapter:
    def __init__(self) -> None:
        self.last_sent: str | None = None

    def send(self, text: str) -> None:
        self.last_sent = text


def test_end_to_end_fake_turn(tmp_path: Path) -> None:
    sender = SenderAdapter()
    orchestrator = PushToTalkOrchestrator(
        capture=CaptureAdapter(),
        stt=SttAdapter(),
        sender=sender,
    )
    result = orchestrator.run_turn(
        wav_path=tmp_path / "turn.wav",
        config=TurnConfig(language="auto"),
        send_text=True,
    )
    assert result.text == "integration transcript"
    assert result.language == "auto"
    assert sender.last_sent == "integration transcript"
