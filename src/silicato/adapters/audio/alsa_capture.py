"""ALSA audio capture adapter."""

from __future__ import annotations

import signal
import subprocess
from pathlib import Path

from silicato.ports.audio import AudioCapturePort


class AlsaCaptureAdapter(AudioCapturePort):
    """Capture adapter backed by `arecord`."""

    def record_once(self, output_path: Path, sample_rate: int, input_device: str | None) -> None:
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
