"""Core runtime profile plugin types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RuntimeSettings:
    model: str
    device: str
    compute_type: str
    reason: str


class RuntimeProfilePlugin(Protocol):
    """Runtime plugin contract for model/device/compute tuning."""

    @property
    def name(self) -> str:
        """Stable plugin identifier."""

    def resolve(self, *, model: str, device: str, compute_type: str) -> RuntimeSettings:
        """Resolve runtime settings for a CLI turn session."""
