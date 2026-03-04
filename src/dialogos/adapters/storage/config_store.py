"""Config storage adapter."""

from __future__ import annotations

from pathlib import Path

from dialogos.config import DialogosConfig as LegacyConfig
from dialogos.config import load_config, save_config
from dialogos.ports.storage import ConfigStorePort, DialogosConfig


class TomlConfigStore(ConfigStorePort):
    """Adapter for persisted TOML configuration."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path

    def load(self) -> DialogosConfig:
        loaded = load_config(self._path)
        return DialogosConfig(tmux_target=loaded.tmux_target)

    def save(self, config: DialogosConfig) -> Path:
        return save_config(LegacyConfig(tmux_target=config.tmux_target), self._path)
