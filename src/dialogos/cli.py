#!/usr/bin/env python3
"""Local push-to-talk transcription loop for Linux."""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from .adapters.tmux_sender import TmuxSender
from .config import DialogosConfig, load_config, save_config
from .contracts import TranscriptResult
from .logging_jsonl import TurnLogEvent, append_turn_log
from .orchestrator import PushToTalkOrchestrator, TurnConfig, parse_confirm_action
from .tmux_picker import (
    InvalidTmuxTargetError,
    NoTmuxSessionError,
    PickerAbortedError,
    list_panes,
    pick_target_interactive,
    print_no_tmux_guidance,
    validate_target,
)


class AlsaCaptureAdapter:
    """Capture adapter backed by `arecord`."""

    def record_once(self, output_path: Path, sample_rate: int, input_device: str | None) -> None:
        record_once(output_path, sample_rate, input_device)


class WhisperSttAdapter:
    """Speech-to-text adapter backed by a loaded faster-whisper model."""

    def __init__(self, model: Any) -> None:
        self._model = model

    def transcribe(self, wav_path: Path, language: str) -> TranscriptResult:
        text = transcribe(self._model, wav_path, language)
        return TranscriptResult(text=text, language=language)


def parse_args() -> argparse.Namespace:
    examples = """Examples:
  dialogos --model small --language auto
  dialogos --pick-target
  dialogos --tmux-target codex:0.1 --preview
  dialogos --doctor
"""
    parser = argparse.ArgumentParser(
        prog="dialogos",
        description="Record mic audio, transcribe locally, and send confirmed text to tmux.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=examples,
    )
    parser.add_argument(
        "--model",
        default="base",
        help=(
            "Whisper model size/name (default: base). Examples: tiny, base, small, medium, large-v3"
        ),
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Inference device: auto, cpu, or cuda (default: cpu).",
    )
    parser.add_argument(
        "--compute-type",
        default="int8",
        help="Compute type passed to faster-whisper (default: int8).",
    )
    parser.add_argument(
        "--language",
        default="auto",
        choices=["de", "en", "auto"],
        help="Language hint (default: auto).",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=16000,
        help="Recording sample rate in Hz (default: 16000).",
    )
    parser.add_argument(
        "--input-device",
        default=None,
        help="Optional ALSA capture device passed to arecord -D (example: hw:0,0).",
    )
    parser.add_argument(
        "--tmux-target",
        default=None,
        help="Explicit tmux target pane (highest priority).",
    )
    parser.add_argument(
        "--pick-target",
        action="store_true",
        help="Always open interactive tmux pane picker at startup.",
    )
    parser.add_argument(
        "--no-remember-target",
        action="store_true",
        help="Do not save chosen target into the config file.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview mode: explicit send only (Enter does not send).",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Override JSONL log path (default uses XDG_STATE_HOME fallback).",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run exactly one completed turn and exit.",
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Print local environment checks and exit.",
    )
    return parser.parse_args()


def require_binary(binary: str, *, apt_package: str) -> None:
    if shutil.which(binary):
        return
    print(f"Missing required binary: {binary}", file=sys.stderr)
    print(f"Install it first (Ubuntu/Debian): sudo apt install {apt_package}", file=sys.stderr)
    raise SystemExit(1)


def record_once(output_path: Path, sample_rate: int, input_device: str | None) -> None:
    cmd = [
        "arecord",
        "-q",
        "-f",
        "S16_LE",
        "-r",
        str(sample_rate),
        "-c",
        "1",
        str(output_path),
    ]
    if input_device:
        cmd[1:1] = ["-D", input_device]

    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    try:
        print("Recording started. Speak now, then press Enter to stop.")
        input()
    except KeyboardInterrupt:
        pass
    finally:
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)
        try:
            _stdout, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            _stdout, stderr = proc.communicate()

    stderr_text = stderr or ""
    stderr_lower = stderr_text.lower()
    benign_interrupt = "interrupted system call" in stderr_lower

    if proc.returncode not in (0, 130, 1):
        details = stderr_text.strip().splitlines()
        short = details[0] if details else "unknown recording error"
        raise RuntimeError(f"arecord failed (exit code {proc.returncode}): {short}")

    if proc.returncode == 1 and not benign_interrupt:
        details = stderr_text.strip().splitlines()
        short = details[0] if details else "unknown recording error"
        raise RuntimeError(f"arecord failed (exit code 1): {short}")

    if stderr_text:
        filtered = [
            line
            for line in stderr_text.splitlines()
            if "Interrupted system call" not in line and line.strip()
        ]
        if filtered:
            print("Recorder message:", " | ".join(filtered))

    try:
        if output_path.stat().st_size < 512:
            raise RuntimeError("No audio captured. Check microphone input and ALSA device.")
    except OSError as exc:
        raise RuntimeError(f"Could not read temporary recording: {exc}") from exc


def is_cuda_runtime_missing(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(
        token in msg
        for token in (
            "libcublas",
            "libcudnn",
            "cuda",
            "cannot be loaded",
            "not found",
        )
    )


def build_model(model_name: str, device: str, compute_type: str) -> tuple[Any, str, str]:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        print("Python package 'faster-whisper' is not installed.", file=sys.stderr)
        print("Run: python3 -m pip install -e .", file=sys.stderr)
        raise SystemExit(1) from exc

    print(
        f"Loading model '{model_name}' (device={device}, compute_type={compute_type}). "
        "First run can take a while due to model download."
    )
    start = time.time()
    try:
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
        elapsed = time.time() - start
        print(f"Model ready in {elapsed:.1f}s.")
        return model, device, compute_type
    except RuntimeError as exc:
        if device in {"auto", "cuda"} and is_cuda_runtime_missing(exc):
            print("CUDA runtime not available. Falling back to CPU (compute_type=int8).")
            model = WhisperModel(model_name, device="cpu", compute_type="int8")
            elapsed = time.time() - start
            print(f"Model ready on CPU in {elapsed:.1f}s.")
            return model, "cpu", "int8"
        raise


def transcribe(model: Any, wav_path: Path, language: str) -> str:
    kwargs: dict[str, object] = {
        "beam_size": 5,
        "vad_filter": True,
        "condition_on_previous_text": False,
    }
    if language.lower() != "auto":
        kwargs["language"] = language

    segments, _info = model.transcribe(str(wav_path), **kwargs)
    return "".join(segment.text for segment in segments).strip()


def run_doctor() -> int:
    print("Environment checks:")
    print(f"- arecord: {'OK' if shutil.which('arecord') else 'MISSING'}")
    print(f"- tmux: {'OK' if shutil.which('tmux') else 'MISSING'}")
    print(f"- ffmpeg: {'OK' if shutil.which('ffmpeg') else 'MISSING'}")
    try:
        from faster_whisper import WhisperModel as _WhisperModel  # noqa: F401

        print("- faster-whisper: OK")
    except ImportError:
        print("- faster-whisper: MISSING (install with: python3 -m pip install -e .)")
    if shutil.which("arecord"):
        print("- ALSA capture devices (arecord -l):")
        result = subprocess.run(["arecord", "-l"], capture_output=True, text=True, check=False)
        text = (result.stdout or result.stderr or "").strip()
        if text:
            for line in text.splitlines()[:20]:
                print(f"  {line}")
        else:
            print("  (no output)")
    return 0


def prompt_turn_start() -> bool:
    try:
        choice = input("Press Enter to talk, or type 'q' then Enter to quit: ").strip().lower()
    except EOFError:
        print()
        return False
    return choice not in {"q", "quit", "exit"}


def prompt_confirm(preview_mode: bool) -> str:
    if preview_mode:
        return input("Confirm [y=send, e=edit, r=retry, s=skip, q=quit]: ")
    return input("Confirm [Enter=send, e=edit, r=retry, s=skip, q=quit]: ")


def prompt_edit_text(current_text: str) -> str:
    print(f"Current transcript: {current_text}")
    edited = input("Edited transcript (empty keeps current): ").strip()
    if edited:
        return edited
    return current_text


def maybe_log(
    *,
    action: str,
    transcript: str,
    language: str,
    tmux_target: str,
    preview: bool,
    sent: bool,
    log_file: Path | None,
) -> None:
    try:
        append_turn_log(
            TurnLogEvent(
                action=action,
                transcript=transcript,
                language=language,
                tmux_target=tmux_target,
                preview=preview,
                sent=sent,
            ),
            path=log_file,
        )
    except OSError as exc:
        print(f"Warning: could not write log file: {exc}", file=sys.stderr)


def resolve_tmux_target(args: argparse.Namespace, remembered_target: str | None) -> str:
    explicit_target = args.tmux_target
    if isinstance(explicit_target, str) and explicit_target:
        validate_target(explicit_target)
        return explicit_target

    if not args.pick_target:
        env_target = os.environ.get("DIALOGOS_TMUX_TARGET")
        if env_target:
            validate_target(env_target)
            return env_target

        if remembered_target:
            try:
                validate_target(remembered_target)
                return remembered_target
            except InvalidTmuxTargetError as exc:
                print(f"Remembered tmux target is invalid: {exc}", file=sys.stderr)
                print("Falling back to interactive picker.", file=sys.stderr)

    panes = list_panes()
    return pick_target_interactive(panes)


def main() -> int:
    args = parse_args()
    if args.doctor:
        return run_doctor()

    require_binary("arecord", apt_package="alsa-utils")
    require_binary("tmux", apt_package="tmux")

    config = load_config()
    try:
        target = resolve_tmux_target(args, config.tmux_target)
    except NoTmuxSessionError:
        print_no_tmux_guidance()
        return 1
    except InvalidTmuxTargetError as exc:
        print(f"Invalid tmux target: {exc}", file=sys.stderr)
        return 1
    except PickerAbortedError:
        print("tmux target selection aborted.", file=sys.stderr)
        return 1

    if not args.no_remember_target and config.tmux_target != target:
        save_config(DialogosConfig(tmux_target=target))

    sender = TmuxSender(target)

    model, active_device, _active_compute_type = build_model(
        args.model, args.device, args.compute_type
    )
    orchestrator = PushToTalkOrchestrator(
        capture=AlsaCaptureAdapter(),
        stt=WhisperSttAdapter(model),
        sender=sender,
    )
    turn_config = TurnConfig(
        sample_rate=args.sample_rate,
        input_device=args.input_device,
        language=args.language,
    )

    while True:
        if not prompt_turn_start():
            return 0

        retry_turn = True
        while retry_turn:
            retry_turn = False
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                wav_path = Path(tmp.name)

            transcript_result: TranscriptResult | None = None
            current_text = ""
            try:
                print("Recording to temporary WAV...")
                transcript_result = orchestrator.run_turn(
                    wav_path,
                    turn_config,
                    send_text=False,
                )
                current_text = transcript_result.text.strip()
            except RuntimeError as exc:
                if active_device in {"auto", "cuda"} and is_cuda_runtime_missing(exc):
                    print("CUDA inference failed during transcription. Retrying on CPU.")
                    model, active_device, _active_compute_type = build_model(
                        args.model, "cpu", "int8"
                    )
                    orchestrator = PushToTalkOrchestrator(
                        capture=AlsaCaptureAdapter(),
                        stt=WhisperSttAdapter(model),
                        sender=sender,
                    )
                    retry_turn = True
                    continue
                print(f"Error: {exc}", file=sys.stderr)
                break
            except Exception as exc:  # noqa: BLE001
                print(f"Error: {exc}", file=sys.stderr)
                break
            finally:
                wav_path.unlink(missing_ok=True)

            if transcript_result is None:
                break
            if not current_text:
                print("Transcript: [no speech detected]")
                maybe_log(
                    action="skip",
                    transcript="",
                    language=transcript_result.language,
                    tmux_target=target,
                    preview=args.preview,
                    sent=False,
                    log_file=args.log_file,
                )
                break

            print(f"Transcript: {current_text}")

            while True:
                action = parse_confirm_action(
                    prompt_confirm(args.preview), preview_mode=args.preview
                )
                if action is None:
                    if args.preview:
                        print("Invalid choice. In preview mode, send must be explicit (type 'y').")
                    else:
                        print("Invalid choice. Press Enter to send or use e/r/s/q.")
                    continue

                if action == "edit":
                    current_text = prompt_edit_text(current_text).strip()
                    if not current_text:
                        print("Transcript is empty. Edit again, retry, skip, or quit.")
                    else:
                        print(f"Edited transcript: {current_text}")
                    continue

                if action == "retry":
                    maybe_log(
                        action="retry",
                        transcript=current_text,
                        language=transcript_result.language,
                        tmux_target=target,
                        preview=args.preview,
                        sent=False,
                        log_file=args.log_file,
                    )
                    retry_turn = True
                    break

                if action == "skip":
                    maybe_log(
                        action="skip",
                        transcript=current_text,
                        language=transcript_result.language,
                        tmux_target=target,
                        preview=args.preview,
                        sent=False,
                        log_file=args.log_file,
                    )
                    break

                if action == "quit":
                    maybe_log(
                        action="quit",
                        transcript=current_text,
                        language=transcript_result.language,
                        tmux_target=target,
                        preview=args.preview,
                        sent=False,
                        log_file=args.log_file,
                    )
                    return 0

                if not current_text:
                    print("Cannot send an empty transcript. Edit, retry, or skip.")
                    continue

                sender.send(current_text)
                maybe_log(
                    action="send",
                    transcript=current_text,
                    language=transcript_result.language,
                    tmux_target=target,
                    preview=args.preview,
                    sent=True,
                    log_file=args.log_file,
                )
                print(f"Sent transcript to tmux target '{target}'.")
                break

            if args.once and not retry_turn:
                return 0


if __name__ == "__main__":
    raise SystemExit(main())
