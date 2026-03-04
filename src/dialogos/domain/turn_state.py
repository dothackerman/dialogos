"""Pure turn state helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TurnConfig:
    sample_rate: int = 16000
    input_device: str | None = None
    language: str = "auto"


def normalize_transcript(text: str) -> str:
    """Normalize transcript text for downstream decisions."""

    return text.strip()
