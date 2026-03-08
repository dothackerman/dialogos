"""Runtime profile resolution for CLI presets."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class RuntimeSettings:
    model: str
    device: str
    compute_type: str
    reason: str


def detect_gpu_total_vram_mb() -> int | None:
    """Return total GPU VRAM in MiB for the first NVIDIA GPU, if available."""

    try:
        proc = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.total",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

    first_line = proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else ""
    if not first_line:
        return None

    try:
        return int(first_line.strip())
    except ValueError:
        return None


def resolve_spawn_profile_settings() -> RuntimeSettings:
    """Resolve a hardware-aware preset tuned for 3-4 parallel instances."""

    total_mb = detect_gpu_total_vram_mb()
    if total_mb is None:
        return RuntimeSettings(
            model="small",
            device="cpu",
            compute_type="int8",
            reason=(
                "spawn profile: no NVIDIA GPU detected; using CPU-safe settings "
                "for multi-instance stability"
            ),
        )

    if total_mb < 5_000:
        return RuntimeSettings(
            model="tiny",
            device="cuda",
            compute_type="int8_float16",
            reason=(
                f"spawn profile: detected {total_mb} MiB VRAM; using tiny/int8_float16 "
                "for 3-4 parallel sessions"
            ),
        )

    if total_mb < 12_000:
        return RuntimeSettings(
            model="small",
            device="cuda",
            compute_type="int8_float16",
            reason=(
                f"spawn profile: detected {total_mb} MiB VRAM; using small/int8_float16 "
                "to support 3-4 parallel sessions"
            ),
        )

    return RuntimeSettings(
        model="base",
        device="cuda",
        compute_type="int8_float16",
        reason=(
            f"spawn profile: detected {total_mb} MiB VRAM; using base/int8_float16 "
            "for 3-4 parallel sessions"
        ),
    )


def apply_profile(
    *,
    profile: str | None,
    model: str,
    device: str,
    compute_type: str,
) -> RuntimeSettings:
    """Apply optional runtime profile to the active CLI settings."""

    if profile != "spawn":
        return RuntimeSettings(
            model=model,
            device=device,
            compute_type=compute_type,
            reason="manual settings",
        )

    return resolve_spawn_profile_settings()
