from __future__ import annotations

import os
import shutil
import subprocess

import pytest


@pytest.mark.hardware
def test_arecord_detects_capture_device() -> None:
    assert shutil.which("arecord"), "arecord not found; install alsa-utils."
    result = subprocess.run(["arecord", "-l"], capture_output=True, text=True, check=False)
    output = "\n".join([result.stdout or "", result.stderr or ""]).lower()
    assert "no soundcards found" not in output, "No ALSA capture device found."


@pytest.mark.hardware
def test_tmux_available() -> None:
    assert shutil.which("tmux"), "tmux not found; install tmux."


@pytest.mark.hardware
def test_tmux_send_smoke_to_temp_pane() -> None:
    assert shutil.which("tmux"), "tmux not found; install tmux."

    session_name = f"dialogos-smoke-{os.getpid()}"
    pane_target = f"{session_name}:0.0"

    try:
        create = subprocess.run(
            ["tmux", "new-session", "-d", "-s", session_name, "cat"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert create.returncode == 0, create.stderr or create.stdout

        payload = "dialogos-hardware-smoke"
        send = subprocess.run(
            ["tmux", "send-keys", "-t", pane_target, payload, "C-m"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert send.returncode == 0, send.stderr or send.stdout

        capture = subprocess.run(
            ["tmux", "capture-pane", "-pt", pane_target],
            capture_output=True,
            text=True,
            check=False,
        )
        assert capture.returncode == 0, capture.stderr or capture.stdout
        assert payload in capture.stdout
    finally:
        _ = subprocess.run(
            ["tmux", "kill-session", "-t", session_name],
            capture_output=True,
            text=True,
            check=False,
        )
