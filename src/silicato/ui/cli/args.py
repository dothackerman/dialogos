"""CLI argument parsing."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    examples = """Examples:
  silicato -m small -l auto
  silicato
  silicato --reuse-target
  silicato -t codex:0.1 -p
  silicato --doctor
"""
    parser = argparse.ArgumentParser(
        prog="silicato",
        description=(
            "Record mic audio, transcribe locally, and send text to tmux "
            "(direct in normal mode, confirmed in preview)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=examples,
    )
    parser.add_argument(
        "-m",
        "--model",
        default="base",
        help=(
            "Whisper model size/name (default: base). Examples: tiny, base, small, medium, large-v3"
        ),
    )
    parser.add_argument(
        "-d",
        "--device",
        default="cpu",
        help="Inference device: auto, cpu, or cuda (default: cpu).",
    )
    parser.add_argument(
        "-c",
        "--compute-type",
        default="int8",
        help="Compute type passed to faster-whisper (default: int8).",
    )
    parser.add_argument(
        "-l",
        "--language",
        default="auto",
        choices=["de", "en", "auto"],
        help="Language hint (default: auto).",
    )
    parser.add_argument(
        "-r",
        "--sample-rate",
        type=int,
        default=16000,
        help="Recording sample rate in Hz (default: 16000).",
    )
    parser.add_argument(
        "-i",
        "--input-device",
        default=None,
        help="Optional ALSA capture device passed to arecord -D (example: hw:0,0).",
    )
    parser.add_argument(
        "-t",
        "--tmux-target",
        default=None,
        help="Explicit tmux target pane (highest priority).",
    )
    picker_mode = parser.add_mutually_exclusive_group()
    picker_mode.add_argument(
        "--pick-target",
        action="store_true",
        default=True,
        help="Open interactive tmux pane picker at startup (default).",
    )
    picker_mode.add_argument(
        "-R",
        "--reuse-target",
        dest="pick_target",
        action="store_false",
        help="Reuse env/config target when available before showing picker.",
    )
    parser.add_argument(
        "-n",
        "--no-remember-target",
        action="store_true",
        help="Do not save chosen target into the config file.",
    )
    parser.add_argument(
        "-p",
        "--preview",
        action="store_true",
        help=("Preview mode: show confirm/edit/retry/skip flow and require explicit send (y)."),
    )
    parser.add_argument(
        "-f",
        "--log-file",
        type=Path,
        default=None,
        help="Override JSONL log path (default uses XDG_STATE_HOME fallback).",
    )
    parser.add_argument(
        "-o",
        "--once",
        action="store_true",
        help="Run exactly one completed turn and exit.",
    )
    parser.add_argument(
        "-D",
        "--doctor",
        action="store_true",
        help="Print local environment checks and exit.",
    )
    return parser.parse_args(argv)
