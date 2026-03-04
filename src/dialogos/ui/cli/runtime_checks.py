"""Runtime checks for local dependencies."""

from __future__ import annotations

import shutil
import subprocess
import sys


def require_binary(binary: str, *, apt_package: str) -> None:
    if shutil.which(binary):
        return
    print(f"Missing required binary: {binary}", file=sys.stderr)
    print(f"Install it first (Ubuntu/Debian): sudo apt install {apt_package}", file=sys.stderr)
    raise SystemExit(1)


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
