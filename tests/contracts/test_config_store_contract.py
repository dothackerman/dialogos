from __future__ import annotations

from pathlib import Path

from silicato.adapters.storage.config_store import TomlConfigStore
from silicato.ports.storage import SilicatoConfig


def test_config_store_contract_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    store = TomlConfigStore(path=path)

    store.save(SilicatoConfig(tmux_target="codex:0.1"))
    loaded = store.load()

    assert loaded.tmux_target == "codex:0.1"


def test_config_store_contract_missing_file_returns_default(tmp_path: Path) -> None:
    store = TomlConfigStore(path=tmp_path / "missing.toml")
    loaded = store.load()

    assert loaded == SilicatoConfig()
