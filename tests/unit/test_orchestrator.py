from __future__ import annotations

from pathlib import Path

from dialogos.contracts import TranscriptResult
from dialogos.orchestrator import PushToTalkOrchestrator, TurnConfig, parse_confirm_action


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


def test_confirm_actions_normal_mode() -> None:
    assert parse_confirm_action("", preview_mode=False) == "send"
    assert parse_confirm_action("e", preview_mode=False) == "edit"
    assert parse_confirm_action("r", preview_mode=False) == "retry"
    assert parse_confirm_action("s", preview_mode=False) == "skip"
    assert parse_confirm_action("q", preview_mode=False) == "quit"


def test_confirm_actions_preview_mode_explicit_send() -> None:
    assert parse_confirm_action("", preview_mode=True) is None
    assert parse_confirm_action("y", preview_mode=True) == "send"
    assert parse_confirm_action("send", preview_mode=True) == "send"
    assert parse_confirm_action("e", preview_mode=True) == "edit"
    assert parse_confirm_action("r", preview_mode=True) == "retry"
    assert parse_confirm_action("s", preview_mode=True) == "skip"
    assert parse_confirm_action("q", preview_mode=True) == "quit"
