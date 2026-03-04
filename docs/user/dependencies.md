# Dependencies

## Runtime
- Linux: Ubuntu 24.04 / TUXEDO OS 24.04 (tier-1 target)
- Python: latest available LTS on target distro (`venv` based)
- `arecord` (ALSA tools)
- `ffmpeg`
- `tmux` (transport target for Codex integration milestone)
- `wl-copy` for Wayland clipboard support

## Python packages
- `faster-whisper` (see `requirements.txt`)

## Optional GPU acceleration
- NVIDIA driver
- CUDA runtime libraries (for example `libcublas12`)

CPU mode remains fully supported and is default-safe.

## Development dependencies
- `ruff` (format + lint)
- `mypy` (type checks)
- `pytest` (unit + integration + hardware tests)

Install with:

```bash
python3 -m pip install -r requirements-dev.txt
```
