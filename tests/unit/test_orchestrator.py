from __future__ import annotations

from pathlib import Path

from dialogos.contracts import TranscriptResult
from dialogos.orchestrator import PushToTalkOrchestrator, TurnConfig


class FakeCapture:
    def __init__(self) -> None:
        self.called = False

    def record_once(self, output_path: Path, sample_rate: int, input_device: str | None) -> None:
        self.called = True
        output_path.write_bytes(b"RIFF....WAVE")
        _ = sample_rate
        _ = input_device


class FakeStt:
    def transcribe(self, wav_path: Path, language: str) -> TranscriptResult:
        _ = wav_path
        return TranscriptResult(text="hello world", language=language)


class FakeSender:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send(self, text: str) -> None:
        self.messages.append(text)


def test_run_turn_without_send(tmp_path: Path) -> None:
    capture = FakeCapture()
    stt = FakeStt()
    orchestrator = PushToTalkOrchestrator(capture=capture, stt=stt, sender=None)
    result = orchestrator.run_turn(
        tmp_path / "turn.wav",
        TurnConfig(language="de"),
        send_text=False,
    )
    assert capture.called
    assert result.text == "hello world"
    assert result.language == "de"


def test_run_turn_with_send(tmp_path: Path) -> None:
    capture = FakeCapture()
    stt = FakeStt()
    sender = FakeSender()
    orchestrator = PushToTalkOrchestrator(capture=capture, stt=stt, sender=sender)
    _ = orchestrator.run_turn(
        tmp_path / "turn.wav",
        TurnConfig(language="en"),
        send_text=True,
    )
    assert sender.messages == ["hello world"]
