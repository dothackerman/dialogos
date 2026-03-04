from __future__ import annotations

from pathlib import Path

import pytest

from dialogos.adapters.storage.config_store import TomlConfigStore, default_config_path
from dialogos.ports.storage import DialogosConfig


def test_default_config_path_uses_xdg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/xdg-config")
    assert default_config_path() == Path("/tmp/xdg-config/dialogos/config.toml")


def test_load_config_missing_returns_default(tmp_path: Path) -> None:
    config = TomlConfigStore(path=tmp_path / "missing.toml").load()
    assert config == DialogosConfig()


def test_save_and_load_config_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    store = TomlConfigStore(path=path)
    store.save(DialogosConfig(tmux_target="codex:0.1"))
    loaded = store.load()
    assert loaded.tmux_target == "codex:0.1"


def test_load_config_rejects_non_string_target(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    path.write_text("tmux_target = 123\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Invalid tmux_target"):
        _ = TomlConfigStore(path=path).load()
