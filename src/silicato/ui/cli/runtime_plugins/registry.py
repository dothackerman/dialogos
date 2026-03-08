"""Runtime profile plugin registry and resolution."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module
from importlib.metadata import entry_points
from typing import Any, cast

from silicato.ui.cli.runtime_plugins.base import RuntimeProfilePlugin, RuntimeSettings

ENTRY_POINT_GROUP = "silicato.runtime_profiles"
_BUILTIN_FALLBACKS = {
    "spawn": "silicato.ui.cli.runtime_plugins.spawn:SpawnRuntimeProfilePlugin",
}


class RuntimeProfilePluginError(RuntimeError):
    """Raised when runtime profile plugin resolution fails."""


@dataclass(frozen=True)
class _CallableRuntimePlugin:
    name: str
    resolver: Callable[..., RuntimeSettings]

    def resolve(self, *, model: str, device: str, compute_type: str) -> RuntimeSettings:
        settings = self.resolver(model=model, device=device, compute_type=compute_type)
        if not isinstance(settings, RuntimeSettings):
            raise RuntimeProfilePluginError(
                f"Plugin '{self.name}' returned invalid settings type: {type(settings).__name__}"
            )
        return settings


def _entrypoint_names() -> set[str]:
    return {ep.name for ep in entry_points().select(group=ENTRY_POINT_GROUP)}


def available_runtime_profiles() -> list[str]:
    names = set()
    names.update(_entrypoint_names())
    for name in _BUILTIN_FALLBACKS:
        if _load_builtin_fallback_plugin(name) is not None:
            names.add(name)
    return sorted(names)


def _coerce_plugin(name: str, loaded: Any) -> RuntimeProfilePlugin:
    plugin_obj = loaded
    if isinstance(plugin_obj, type):
        plugin_obj = plugin_obj()

    if callable(plugin_obj) and not hasattr(plugin_obj, "resolve"):
        return _CallableRuntimePlugin(name=name, resolver=plugin_obj)

    if hasattr(plugin_obj, "resolve") and callable(plugin_obj.resolve):
        return cast(RuntimeProfilePlugin, plugin_obj)

    raise RuntimeProfilePluginError(
        f"Plugin '{name}' does not expose a callable resolver (expected .resolve() or callable)."
    )


def _load_entrypoint_plugin(name: str) -> RuntimeProfilePlugin | None:
    matches = [ep for ep in entry_points().select(group=ENTRY_POINT_GROUP) if ep.name == name]
    if not matches:
        return None
    if len(matches) > 1:
        raise RuntimeProfilePluginError(
            f"Multiple entry-point plugins found for '{name}'. Keep plugin names unique."
        )

    entry_point = matches[0]
    try:
        loaded = entry_point.load()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeProfilePluginError(f"Failed to load plugin '{name}': {exc}") from exc

    return _coerce_plugin(name, loaded)


def _load_builtin_fallback_plugin(name: str) -> RuntimeProfilePlugin | None:
    target = _BUILTIN_FALLBACKS.get(name)
    if target is None:
        return None

    module_name, _, attr_name = target.partition(":")
    if not module_name or not attr_name:
        raise RuntimeProfilePluginError(f"Invalid builtin fallback target for '{name}': {target}")

    try:
        module = import_module(module_name)
        loaded = getattr(module, attr_name)
    except (ImportError, AttributeError):
        return None

    return _coerce_plugin(name, loaded)


def resolve_runtime_settings(
    *,
    profile: str | None,
    model: str,
    device: str,
    compute_type: str,
) -> RuntimeSettings:
    if profile is None:
        return RuntimeSettings(
            model=model,
            device=device,
            compute_type=compute_type,
            reason="manual settings",
        )

    plugin = _load_entrypoint_plugin(profile)
    if plugin is None:
        plugin = _load_builtin_fallback_plugin(profile)

    if plugin is None:
        available = ", ".join(available_runtime_profiles()) or "(none)"
        raise RuntimeProfilePluginError(
            f"Unknown runtime profile plugin '{profile}'. Available plugins: {available}"
        )

    try:
        settings = plugin.resolve(model=model, device=device, compute_type=compute_type)
    except RuntimeProfilePluginError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise RuntimeProfilePluginError(f"Plugin '{profile}' failed: {exc}") from exc

    if not isinstance(settings, RuntimeSettings):
        raise RuntimeProfilePluginError(
            f"Plugin '{profile}' returned invalid settings type: {type(settings).__name__}"
        )
    return settings
