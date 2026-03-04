from __future__ import annotations

from argparse import Namespace
from pathlib import Path

import pytest

import dialogos.cli as cli
from dialogos.config import DialogosConfig, load_config, save_config
from dialogos.contracts import TranscriptResult
from dialogos.orchestrator import PushToTalkOrchestrator, TurnConfig, parse_confirm_action


class CaptureAdapter:
    def __init__(self) -> None:
        self.calls = 0

    def record_once(self, output_path: Path, sample_rate: int, input_device: str | None) -> None:
        self.calls += 1
        output_path.write_bytes(b"RIFF....WAVE")
        _ = sample_rate
        _ = input_device


class SttAdapter:
    def __init__(self, transcripts: list[str]) -> None:
        self._transcripts = transcripts
        self._index = 0

    def transcribe(self, wav_path: Path, language: str) -> TranscriptResult:
        _ = wav_path
        text = self._transcripts[self._index]
        self._index += 1
        return TranscriptResult(text=text, language=language)


class SenderAdapter:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def send(self, text: str) -> None:
        self.messages.append(text)


def run_fake_turn(
    *,
    orchestrator: PushToTalkOrchestrator,
    tmp_path: Path,
    decision_inputs: list[str],
    edit_inputs: list[str],
) -> tuple[str, str | None]:
    decisions = iter(decision_inputs)
    edits = iter(edit_inputs)
    turn_index = 0

    while True:
        result = orchestrator.run_turn(
            wav_path=tmp_path / f"turn-{turn_index}.wav",
            config=TurnConfig(language="auto"),
            send_text=False,
        )
        turn_index += 1
        current_text = result.text

        while True:
            action = parse_confirm_action(next(decisions), preview_mode=False)
            assert action is not None
            if action == "edit":
                current_text = next(edits)
                continue
            if action == "retry":
                break
            if action == "skip":
                return "skip", None
            if action == "quit":
                return "quit", None
            sender = orchestrator.sender
            assert sender is not None
            sender.send(current_text)
            return "send", current_text


def test_end_to_end_fake_turn_send_edit_retry_skip(tmp_path: Path) -> None:
    # send
    sender = SenderAdapter()
    send_orchestrator = PushToTalkOrchestrator(
        capture=CaptureAdapter(),
        stt=SttAdapter(["integration transcript"]),
        sender=sender,
    )
    action, sent_text = run_fake_turn(
        orchestrator=send_orchestrator,
        tmp_path=tmp_path,
        decision_inputs=[""],
        edit_inputs=[],
    )
    assert action == "send"
    assert sent_text == "integration transcript"
    assert sender.messages == ["integration transcript"]

    # edit then send
    sender = SenderAdapter()
    edit_orchestrator = PushToTalkOrchestrator(
        capture=CaptureAdapter(),
        stt=SttAdapter(["raw text"]),
        sender=sender,
    )
    action, sent_text = run_fake_turn(
        orchestrator=edit_orchestrator,
        tmp_path=tmp_path,
        decision_inputs=["e", ""],
        edit_inputs=["edited text"],
    )
    assert action == "send"
    assert sent_text == "edited text"
    assert sender.messages == ["edited text"]

    # retry then send
    sender = SenderAdapter()
    retry_capture = CaptureAdapter()
    retry_orchestrator = PushToTalkOrchestrator(
        capture=retry_capture,
        stt=SttAdapter(["first", "second"]),
        sender=sender,
    )
    action, sent_text = run_fake_turn(
        orchestrator=retry_orchestrator,
        tmp_path=tmp_path,
        decision_inputs=["r", ""],
        edit_inputs=[],
    )
    assert action == "send"
    assert sent_text == "second"
    assert sender.messages == ["second"]
    assert retry_capture.calls == 2

    # skip
    sender = SenderAdapter()
    skip_orchestrator = PushToTalkOrchestrator(
        capture=CaptureAdapter(),
        stt=SttAdapter(["discard me"]),
        sender=sender,
    )
    action, sent_text = run_fake_turn(
        orchestrator=skip_orchestrator,
        tmp_path=tmp_path,
        decision_inputs=["s"],
        edit_inputs=[],
    )
    assert action == "skip"
    assert sent_text is None
    assert sender.messages == []


def test_remembered_target_reuse_and_cli_override(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.toml"
    save_config(DialogosConfig(tmux_target="remembered:0.1"), config_path)
    loaded = load_config(config_path)
    assert loaded.tmux_target == "remembered:0.1"

    validated: list[str] = []

    def fake_validate(target: str) -> None:
        validated.append(target)

    monkeypatch.setattr(cli, "validate_target", fake_validate)
    monkeypatch.delenv("DIALOGOS_TMUX_TARGET", raising=False)

    args = Namespace(tmux_target=None, pick_target=False)
    resolved = cli.resolve_tmux_target(args, remembered_target=loaded.tmux_target)
    assert resolved == "remembered:0.1"

    override_args = Namespace(tmux_target="override:0.2", pick_target=False)
    override = cli.resolve_tmux_target(override_args, remembered_target=loaded.tmux_target)
    assert override == "override:0.2"
    assert validated == ["remembered:0.1", "override:0.2"]
