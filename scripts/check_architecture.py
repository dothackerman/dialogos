#!/usr/bin/env python3
"""Validate layered import boundaries for the Dialogos codebase."""

from __future__ import annotations

import argparse
import ast
import sys
import tomllib
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ArchitectureRules:
    rules_path: Path
    root_package: str
    source_root: Path
    layers: tuple[str, ...]
    forbidden: dict[str, set[str]]
    forbidden_module_prefixes: tuple[str, ...]


@dataclass(frozen=True)
class ImportUse:
    module: str
    line: int
    column: int


@dataclass(frozen=True)
class Violation:
    file_path: Path
    line: int
    column: int
    source_layer: str
    target_layer: str | None
    imported_module: str
    violation_type: str


@dataclass(frozen=True)
class ParseError:
    file_path: Path
    line: int
    column: int
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check layered architecture import boundaries.",
    )
    parser.add_argument(
        "--rules",
        type=Path,
        default=Path("architecture_rules.toml"),
        help="Path to architecture rules TOML file (default: architecture_rules.toml).",
    )
    return parser.parse_args()


def load_rules(rules_path: Path) -> ArchitectureRules:
    if not rules_path.exists():
        raise ValueError(f"Rules file not found: {rules_path}")

    try:
        raw = tomllib.loads(rules_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Invalid TOML in {rules_path}: {exc}") from exc

    root_package = raw.get("root_package")
    source_root_value = raw.get("source_root")
    layers_value = raw.get("layers")
    forbidden_value = raw.get("forbidden")
    forbidden_module_prefixes_value = raw.get("forbidden_module_prefixes", [])

    if not isinstance(root_package, str) or not root_package:
        raise ValueError("'root_package' must be a non-empty string")
    if not isinstance(source_root_value, str) or not source_root_value:
        raise ValueError("'source_root' must be a non-empty string")
    if not isinstance(layers_value, list) or not all(
        isinstance(item, str) for item in layers_value
    ):
        raise ValueError("'layers' must be a list of strings")
    if not isinstance(forbidden_value, dict):
        raise ValueError("'forbidden' must be a table mapping layer -> [layers]")
    if not isinstance(forbidden_module_prefixes_value, list) or not all(
        isinstance(item, str) and item for item in forbidden_module_prefixes_value
    ):
        raise ValueError("'forbidden_module_prefixes' must be a list of non-empty strings")

    layers = tuple(layers_value)
    unknown_layers = sorted(layer for layer in forbidden_value if layer not in layers)
    if unknown_layers:
        raise ValueError(f"Unknown layers in [forbidden]: {', '.join(unknown_layers)}")

    forbidden: dict[str, set[str]] = {}
    for layer in layers:
        blocked_layers = forbidden_value.get(layer, [])
        if not isinstance(blocked_layers, list) or not all(
            isinstance(item, str) for item in blocked_layers
        ):
            raise ValueError(f"forbidden.{layer} must be a list of strings")

        invalid_targets = sorted(target for target in blocked_layers if target not in layers)
        if invalid_targets:
            joined = ", ".join(invalid_targets)
            raise ValueError(f"forbidden.{layer} contains unknown layers: {joined}")

        forbidden[layer] = set(blocked_layers)

    source_root = (rules_path.parent / source_root_value).resolve()
    if not source_root.exists():
        raise ValueError(f"Configured source_root does not exist: {source_root}")

    return ArchitectureRules(
        rules_path=rules_path.resolve(),
        root_package=root_package,
        source_root=source_root,
        layers=layers,
        forbidden=forbidden,
        forbidden_module_prefixes=tuple(forbidden_module_prefixes_value),
    )


def iter_python_files(source_root: Path) -> list[Path]:
    return sorted(path for path in source_root.rglob("*.py") if path.is_file())


def module_name_for_file(file_path: Path, rules: ArchitectureRules) -> str:
    relative = file_path.relative_to(rules.source_root)
    parts = list(relative.parts)
    if not parts:
        return rules.root_package

    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = Path(parts[-1]).stem

    suffix = ".".join(parts)
    return rules.root_package if not suffix else f"{rules.root_package}.{suffix}"


def package_name_for_file(file_path: Path, module_name: str) -> str:
    if file_path.name == "__init__.py":
        return module_name
    return module_name.rpartition(".")[0]


def layer_for_file(file_path: Path, rules: ArchitectureRules) -> str | None:
    relative = file_path.relative_to(rules.source_root)
    if not relative.parts:
        return None

    first_segment = relative.parts[0]
    if first_segment in rules.layers:
        return first_segment

    return None


def layer_for_module(module_name: str, rules: ArchitectureRules) -> str | None:
    if module_name == rules.root_package:
        return None

    prefix = f"{rules.root_package}."
    if not module_name.startswith(prefix):
        return None

    remainder = module_name[len(prefix) :]
    first_segment = remainder.split(".", maxsplit=1)[0]
    if first_segment in rules.layers:
        return first_segment

    return None


def resolve_import_from_base(node: ast.ImportFrom, current_package: str) -> str | None:
    if node.level == 0:
        return node.module

    if not current_package:
        return None

    package_parts = current_package.split(".")
    parents_to_trim = node.level - 1
    if parents_to_trim > len(package_parts):
        return None

    kept_parts = package_parts[: len(package_parts) - parents_to_trim]
    if node.module:
        kept_parts.extend(node.module.split("."))

    return ".".join(part for part in kept_parts if part)


def modules_from_import_from(
    node: ast.ImportFrom,
    current_package: str,
    rules: ArchitectureRules,
) -> list[str]:
    base_module = resolve_import_from_base(node, current_package)
    if not base_module:
        return []

    if layer_for_module(base_module, rules) is not None:
        return [base_module]

    resolved_modules: list[str] = []
    for alias in node.names:
        if alias.name == "*":
            continue
        resolved_modules.append(f"{base_module}.{alias.name}")

    return resolved_modules


def collect_imports(
    tree: ast.AST,
    current_package: str,
    rules: ArchitectureRules,
) -> list[ImportUse]:
    found: list[ImportUse] = []
    seen: set[tuple[str, int, int]] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                key = (alias.name, node.lineno, node.col_offset)
                if key in seen:
                    continue
                seen.add(key)
                found.append(
                    ImportUse(module=alias.name, line=node.lineno, column=node.col_offset + 1)
                )

        if isinstance(node, ast.ImportFrom):
            for module_name in modules_from_import_from(node, current_package, rules):
                key = (module_name, node.lineno, node.col_offset)
                if key in seen:
                    continue
                seen.add(key)
                found.append(
                    ImportUse(module=module_name, line=node.lineno, column=node.col_offset + 1)
                )

    return found


def matches_module_prefix(module_name: str, prefix: str) -> bool:
    return module_name == prefix or module_name.startswith(f"{prefix}.")


def check_file(
    file_path: Path, rules: ArchitectureRules
) -> tuple[list[Violation], ParseError | None]:
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as exc:
        return [], ParseError(
            file_path=file_path,
            line=exc.lineno or 0,
            column=exc.offset or 0,
            message=exc.msg,
        )

    source_layer = layer_for_file(file_path, rules)
    if source_layer is None:
        return [], None

    module_name = module_name_for_file(file_path, rules)
    current_package = package_name_for_file(file_path, module_name)

    violations: list[Violation] = []
    forbidden_targets = rules.forbidden.get(source_layer, set())

    for imported in collect_imports(tree, current_package, rules):
        if any(
            matches_module_prefix(imported.module, prefix)
            for prefix in rules.forbidden_module_prefixes
        ):
            violations.append(
                Violation(
                    file_path=file_path,
                    line=imported.line,
                    column=imported.column,
                    source_layer=source_layer,
                    target_layer=None,
                    imported_module=imported.module,
                    violation_type="module",
                )
            )
            continue

        target_layer = layer_for_module(imported.module, rules)
        if target_layer is None:
            continue
        if target_layer not in forbidden_targets:
            continue

        violations.append(
            Violation(
                file_path=file_path,
                line=imported.line,
                column=imported.column,
                source_layer=source_layer,
                target_layer=target_layer,
                imported_module=imported.module,
                violation_type="layer",
            )
        )

    return violations, None


def check_architecture(rules: ArchitectureRules) -> tuple[list[Violation], list[ParseError], int]:
    violations: list[Violation] = []
    parse_errors: list[ParseError] = []

    files = iter_python_files(rules.source_root)
    for file_path in files:
        file_violations, parse_error = check_file(file_path, rules)
        violations.extend(file_violations)
        if parse_error is not None:
            parse_errors.append(parse_error)

    violations.sort(
        key=lambda item: (str(item.file_path), item.line, item.column, item.imported_module)
    )
    parse_errors.sort(key=lambda item: (str(item.file_path), item.line, item.column))
    return violations, parse_errors, len(files)


def format_path(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def layer_violation_hint(source_layer: str, target_layer: str) -> str:
    if source_layer == "application" and target_layer == "adapters":
        return "Depend on a contract in dialogos.ports and inject the adapter from dialogos.ui."
    if source_layer == "ui" and target_layer == "domain":
        return "Call an application use-case instead of importing domain internals directly."
    if target_layer == "ui":
        return "Move CLI concerns out of lower layers and keep them in dialogos.ui."
    return "Move the dependency to an allowed layer or invert it through dialogos.ports."


def module_violation_hint(imported_module: str) -> str:
    if imported_module.startswith("dialogos.config"):
        return "Use dialogos.adapters.storage.config_store instead."
    if imported_module.startswith("dialogos.logging_jsonl"):
        return "Use dialogos.adapters.storage.jsonl_turn_logger instead."
    if imported_module.startswith("dialogos.tmux_picker"):
        return "Use dialogos.adapters.tmux.target_resolver instead."
    if imported_module.startswith("dialogos.orchestrator"):
        return "Use dialogos.application.use_cases modules instead."
    if imported_module.startswith("dialogos.contracts"):
        return "Use dialogos.ports contracts instead."
    if imported_module.startswith("dialogos.adapters.tmux_sender"):
        return "Use dialogos.adapters.tmux.sender instead."
    return "Use canonical layered modules and avoid forbidden compatibility paths."


def print_report(
    violations: Iterable[Violation],
    parse_errors: Iterable[ParseError],
    rules: ArchitectureRules,
) -> None:
    project_root = rules.rules_path.parent
    parse_errors = list(parse_errors)
    violations = list(violations)

    if parse_errors:
        print("Architecture check failed: unable to parse Python files:", file=sys.stderr)
        for error in parse_errors:
            location = format_path(error.file_path, project_root)
            print(
                f"- {location}:{error.line}:{error.column}: {error.message}",
                file=sys.stderr,
            )

    if violations:
        print(f"Architecture check failed: {len(violations)} violation(s):", file=sys.stderr)
        for violation in violations:
            location = format_path(violation.file_path, project_root)
            if violation.violation_type == "layer":
                assert violation.target_layer is not None
                print(
                    (
                        f"- {location}:{violation.line}:{violation.column}: "
                        f"{violation.source_layer} -> {violation.target_layer} is forbidden "
                        f"(import '{violation.imported_module}')"
                    ),
                    file=sys.stderr,
                )
                print(
                    (
                        "  Fix: "
                        f"{layer_violation_hint(violation.source_layer, violation.target_layer)}"
                    ),
                    file=sys.stderr,
                )
                continue

            print(
                (
                    f"- {location}:{violation.line}:{violation.column}: "
                    f"{violation.source_layer} imports forbidden module "
                    f"'{violation.imported_module}'"
                ),
                file=sys.stderr,
            )
            print(
                f"  Fix: {module_violation_hint(violation.imported_module)}",
                file=sys.stderr,
            )


def main() -> int:
    args = parse_args()

    try:
        rules = load_rules(args.rules.resolve())
    except ValueError as exc:
        print(f"Architecture check configuration error: {exc}", file=sys.stderr)
        return 2

    violations, parse_errors, scanned_files = check_architecture(rules)
    if violations or parse_errors:
        print_report(violations, parse_errors, rules)
        return 1

    print(f"Architecture check passed: scanned {scanned_files} Python file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
