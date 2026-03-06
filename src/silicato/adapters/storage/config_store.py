"""Config storage adapter."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from silicato.ports.storage import ConfigStorePort, SilicatoConfig


def default_config_path() -> Path:
    """Resolve the default configuration path using XDG conventions."""

    xdg_root = os.environ.get("XDG_CONFIG_HOME")
    if xdg_root:
        return Path(xdg_root) / "silicato" / "config.toml"
    return Path.home() / ".config" / "silicato" / "config.toml"


class TomlConfigStore(ConfigStorePort):
    """Adapter for persisted TOML configuration."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path

    def load(self) -> SilicatoConfig:
        config_path = self._path or default_config_path()
        if not config_path.exists():
            return SilicatoConfig()

        try:
            data = tomllib.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise RuntimeError(f"Failed to load config file at {config_path}: {exc}") from exc

        raw_target = data.get("tmux_target")
        if raw_target is None:
            return SilicatoConfig()
        if not isinstance(raw_target, str):
            raise RuntimeError(f"Invalid tmux_target in {config_path}: expected string")
        target = raw_target.strip()
        if not target:
            return SilicatoConfig()
        return SilicatoConfig(tmux_target=target)

    def save(self, config: SilicatoConfig) -> Path:
        config_path = self._path or default_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = []
        if config.tmux_target:
            escaped = config.tmux_target.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'tmux_target = "{escaped}"')

        payload = "\n".join(lines) + "\n"
        config_path.write_text(payload, encoding="utf-8")
        return config_path
