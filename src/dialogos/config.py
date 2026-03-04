"""Configuration persistence for Dialogos."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DialogosConfig:
    """Persisted user configuration."""

    tmux_target: str | None = None


def default_config_path() -> Path:
    """Resolve the default configuration path using XDG conventions."""

    xdg_root = os.environ.get("XDG_CONFIG_HOME")
    if xdg_root:
        return Path(xdg_root) / "dialogos" / "config.toml"
    return Path.home() / ".config" / "dialogos" / "config.toml"


def load_config(path: Path | None = None) -> DialogosConfig:
    """Load configuration from TOML, returning defaults when absent."""

    config_path = path or default_config_path()
    if not config_path.exists():
        return DialogosConfig()

    try:
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise RuntimeError(f"Failed to load config file at {config_path}: {exc}") from exc

    raw_target = data.get("tmux_target")
    if raw_target is None:
        return DialogosConfig()
    if not isinstance(raw_target, str):
        raise RuntimeError(f"Invalid tmux_target in {config_path}: expected string")
    target = raw_target.strip()
    if not target:
        return DialogosConfig()
    return DialogosConfig(tmux_target=target)


def save_config(config: DialogosConfig, path: Path | None = None) -> Path:
    """Persist configuration to TOML."""

    config_path = path or default_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    if config.tmux_target:
        escaped = config.tmux_target.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'tmux_target = "{escaped}"')

    payload = "\n".join(lines) + "\n"
    config_path.write_text(payload, encoding="utf-8")
    return config_path
