from __future__ import annotations

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
