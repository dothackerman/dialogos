from __future__ import annotations

import os
import shutil
import subprocess

import pytest

from silicato.adapters.tmux.runtime import TmuxRuntime


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

    runtime = TmuxRuntime()
    session_name = f"silicato-smoke-{os.getpid()}"
    pane_target = f"{session_name}:0.0"

    try:
        create = runtime.new_session(session_name, command="cat")
        assert create.returncode == 0, create.stderr or create.stdout

        payload = "silicato-hardware-smoke"
        send = runtime.send_keys(pane_target, payload, "C-m")
        assert send.returncode == 0, send.stderr or send.stdout

        capture = runtime.capture_pane(pane_target)
        assert capture.returncode == 0, capture.stderr or capture.stdout
        assert payload in capture.stdout
    finally:
        _ = runtime.kill_session(session_name)
