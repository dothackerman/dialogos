# Dependencies

## Runtime
- Linux: Ubuntu 24.04 / TUXEDO OS 24.04 (tier-1 target)
- Python: 3.12+
- `arecord` (`alsa-utils`)
- `ffmpeg`
- `tmux`

## Python packages (managed in `pyproject.toml`)
- Runtime: `faster-whisper`
- Dev extra (`.[dev]`): `ruff`, `mypy`, `pytest`

Install commands:

```bash
python3 -m pip install -e .
python3 -m pip install -e .[dev]
```

## Optional GPU acceleration
- NVIDIA driver
- CUDA runtime libraries (for example `libcublas12`)

CPU mode remains supported and is the safe default.

## tmux requirement behavior
- Dialogos validates target pane before send
- If no tmux session exists, Dialogos shows guided setup and exits non-zero
