from __future__ import annotations

from pathlib import Path

import pytest

from dialogos.config import DialogosConfig, default_config_path, load_config, save_config


def test_default_config_path_uses_xdg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", "/tmp/xdg-config")
    assert default_config_path() == Path("/tmp/xdg-config/dialogos/config.toml")


def test_load_config_missing_returns_default(tmp_path: Path) -> None:
    config = load_config(tmp_path / "missing.toml")
    assert config == DialogosConfig()


def test_save_and_load_config_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    save_config(DialogosConfig(tmux_target="codex:0.1"), path)
    loaded = load_config(path)
    assert loaded.tmux_target == "codex:0.1"


def test_load_config_rejects_non_string_target(tmp_path: Path) -> None:
    path = tmp_path / "config.toml"
    path.write_text("tmux_target = 123\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="Invalid tmux_target"):
        _ = load_config(path)
