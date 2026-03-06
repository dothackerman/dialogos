"""Audio capture port."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


class AudioCapturePort(Protocol):
    """Capability for recording one audio turn."""

    def record_once(
        self, output_path: Path, sample_rate: int, input_device: str | None
    ) -> None: ...
