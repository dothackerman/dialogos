from __future__ import annotations

import pytest

from silicato.ui.cli.runtime_plugins import (
    RuntimeProfilePluginError,
    registry,
    resolve_runtime_settings,
)


def test_resolve_runtime_settings_returns_manual_settings_when_profile_absent() -> None:
    settings = resolve_runtime_settings(
        profile=None,
        model="medium",
        device="cuda",
        compute_type="float16",
    )
    assert settings.model == "medium"
    assert settings.device == "cuda"
    assert settings.compute_type == "float16"
    assert settings.reason == "manual settings"


def test_resolve_runtime_settings_spawn_cpu_fallback_when_no_gpu(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "silicato.ui.cli.runtime_plugins.spawn.SpawnRuntimeProfilePlugin._detect_gpu_total_vram_mb",
        lambda *_args: None,
    )

    settings = resolve_runtime_settings(
        profile="spawn",
        model="medium",
        device="cuda",
        compute_type="float16",
    )

    assert settings.model == "small"
    assert settings.device == "cpu"
    assert settings.compute_type == "int8"
    assert "no NVIDIA GPU" in settings.reason


def test_resolve_runtime_settings_spawn_6gb_gpu_prefers_small_int8_float16(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "silicato.ui.cli.runtime_plugins.spawn.SpawnRuntimeProfilePlugin._detect_gpu_total_vram_mb",
        lambda *_args: 6144,
    )

    settings = resolve_runtime_settings(
        profile="spawn",
        model="medium",
        device="cuda",
        compute_type="float16",
    )

    assert settings.model == "small"
    assert settings.device == "cuda"
    assert settings.compute_type == "int8_float16"
    assert "6144" in settings.reason


def test_resolve_runtime_settings_unknown_plugin_raises_with_available_names() -> None:
    with pytest.raises(RuntimeProfilePluginError) as exc:
        resolve_runtime_settings(
            profile="missing-plugin",
            model="medium",
            device="cuda",
            compute_type="float16",
        )
    assert "Unknown runtime profile plugin 'missing-plugin'" in str(exc.value)
    assert "spawn" in str(exc.value)


def test_available_runtime_profiles_includes_entrypoint_plugins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeEntryPoint:
        def __init__(self, name: str) -> None:
            self.name = name

        def load(self) -> object:
            raise RuntimeError("not needed")

    class _FakeEntryPoints(list[_FakeEntryPoint]):
        def select(self, *, group: str | None = None) -> _FakeEntryPoints:
            if group == registry.ENTRY_POINT_GROUP:
                return self
            return _FakeEntryPoints()

    monkeypatch.setattr(
        registry, "entry_points", lambda: _FakeEntryPoints([_FakeEntryPoint("eco")])
    )
    assert registry.available_runtime_profiles() == ["eco", "spawn"]


def test_resolve_runtime_settings_uses_callable_entrypoint_plugin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeEntryPoint:
        def __init__(self, name: str) -> None:
            self.name = name

        def load(self) -> object:
            def _resolve(**_kwargs: str) -> registry.RuntimeSettings:
                return registry.RuntimeSettings(
                    model="tiny",
                    device="cpu",
                    compute_type="int8",
                    reason="eco plugin selected",
                )

            return _resolve

    class _FakeEntryPoints(list[_FakeEntryPoint]):
        def select(self, *, group: str | None = None) -> _FakeEntryPoints:
            if group == registry.ENTRY_POINT_GROUP:
                return self
            return _FakeEntryPoints()

    monkeypatch.setattr(
        registry, "entry_points", lambda: _FakeEntryPoints([_FakeEntryPoint("eco")])
    )
    settings = resolve_runtime_settings(
        profile="eco",
        model="medium",
        device="cuda",
        compute_type="float16",
    )
    assert settings.reason == "eco plugin selected"
