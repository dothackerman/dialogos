"""ALSA audio capture adapter."""

from __future__ import annotations

import audioop
import os
import select
import signal
import subprocess
import sys
import time
from pathlib import Path

from silicato.ports.audio import AudioCapturePort


class AlsaCaptureAdapter(AudioCapturePort):
    """Capture adapter backed by `arecord`."""

    def __init__(
        self,
        *,
        silence_stop_seconds: float = 1.8,
        silence_rms_threshold: int = 500,
        poll_interval_seconds: float = 0.1,
    ) -> None:
        self._silence_stop_seconds = max(0.0, float(silence_stop_seconds))
        self._silence_rms_threshold = max(1, int(silence_rms_threshold))
        self._poll_interval_seconds = max(0.02, float(poll_interval_seconds))

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
            self._wait_for_stop(proc, output_path)
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

    def _wait_for_stop(self, proc: subprocess.Popen[str], output_path: Path) -> None:
        if self._silence_stop_seconds <= 0:
            print("Recording started. Speak now, then press Enter to stop.")
            input()
            return

        print(
            "Recording started. Speak now. "
            f"Auto-stop after {self._silence_stop_seconds:.1f}s of silence "
            "(press Enter to stop manually)."
        )

        read_offset = 44  # Skip WAV header while sampling PCM amplitude.
        speech_seen = False
        last_voice_at: float | None = None

        while proc.poll() is None:
            if _stdin_line_ready():
                _consume_stdin_line()
                return

            pcm_chunk = _read_new_pcm(output_path, read_offset)
            if pcm_chunk:
                read_offset += len(pcm_chunk)
                if len(pcm_chunk) % 2 == 1:
                    pcm_chunk = pcm_chunk[:-1]
                if pcm_chunk:
                    rms = audioop.rms(pcm_chunk, 2)
                    now = time.monotonic()
                    if rms >= self._silence_rms_threshold:
                        speech_seen = True
                        last_voice_at = now
                    elif speech_seen and last_voice_at is not None:
                        if now - last_voice_at >= self._silence_stop_seconds:
                            return
            elif speech_seen and last_voice_at is not None:
                if time.monotonic() - last_voice_at >= self._silence_stop_seconds:
                    return

            time.sleep(self._poll_interval_seconds)


def _stdin_line_ready() -> bool:
    try:
        fd = sys.stdin.fileno()
    except (AttributeError, OSError):
        return False
    if not os.isatty(fd):
        return False
    readable, _, _ = select.select([sys.stdin], [], [], 0.0)
    return bool(readable)


def _consume_stdin_line() -> None:
    try:
        sys.stdin.readline()
    except OSError:
        return


def _read_new_pcm(path: Path, offset: int) -> bytes:
    try:
        size = path.stat().st_size
    except OSError:
        return b""
    if size <= offset:
        return b""
    try:
        with path.open("rb") as handle:
            handle.seek(offset)
            return handle.read(size - offset)
    except OSError:
        return b""
