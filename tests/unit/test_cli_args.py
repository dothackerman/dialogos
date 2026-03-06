from __future__ import annotations

from pathlib import Path

from silicato.ui.cli.args import parse_args


def test_parse_args_supports_short_options() -> None:
    args = parse_args(
        [
            "-m",
            "small",
            "-d",
            "auto",
            "-c",
            "float16",
            "-l",
            "de",
            "-r",
            "44100",
            "-i",
            "hw:0,0",
            "-t",
            "codex:0.1",
            "-n",
            "-p",
            "-f",
            "/tmp/silicato.jsonl",
            "-o",
            "-D",
        ]
    )

    assert args.model == "small"
    assert args.device == "auto"
    assert args.compute_type == "float16"
    assert args.language == "de"
    assert args.sample_rate == 44100
    assert args.input_device == "hw:0,0"
    assert args.tmux_target == "codex:0.1"
    assert args.no_remember_target is True
    assert args.preview is True
    assert args.log_file == Path("/tmp/silicato.jsonl")
    assert args.once is True
    assert args.doctor is True


def test_parse_args_picker_is_default_and_reuse_can_be_opted_in() -> None:
    default_args = parse_args([])
    assert default_args.pick_target is True

    reuse_args = parse_args(["--reuse-target"])
    assert reuse_args.pick_target is False
