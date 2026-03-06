#!/usr/bin/env python3
"""Validate and execute Silicato business-rule regression mappings."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Rule:
    rule_id: str
    statement: str
    owner_layer: str
    requires_hardware: bool
    tests: tuple[str, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check and run business-rule regression mappings.",
    )
    parser.add_argument(
        "--rules",
        type=Path,
        default=Path("docs/dev/business-rules.toml"),
        help="Path to business rules catalog TOML (default: docs/dev/business-rules.toml).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check", help="Validate rule schema and mapped pytest nodes.")

    test_parser = subparsers.add_parser("test", help="Run pytest for mapped rule nodes.")
    test_parser.add_argument(
        "--fast",
        action="store_true",
        help="Run only non-hardware rules and exclude pytest hardware marker.",
    )
    return parser.parse_args()


def load_rules(catalog_path: Path) -> list[Rule]:
    if not catalog_path.exists():
        raise ValueError(f"Rules catalog not found: {catalog_path}")

    try:
        raw = tomllib.loads(catalog_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"Invalid TOML in {catalog_path}: {exc}") from exc

    raw_rules = raw.get("rule")
    if not isinstance(raw_rules, list) or not raw_rules:
        raise ValueError("Catalog must define at least one [[rule]] entry")

    seen_ids: set[str] = set()
    parsed: list[Rule] = []

    for index, item in enumerate(raw_rules, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"rule[{index}] must be a TOML table")

        rule_id = item.get("id")
        statement = item.get("statement")
        owner_layer = item.get("owner_layer")
        requires_hardware = item.get("requires_hardware", False)
        tests = item.get("tests")

        if not isinstance(rule_id, str) or not rule_id:
            raise ValueError(f"rule[{index}] has invalid 'id'")
        if rule_id in seen_ids:
            raise ValueError(f"Duplicate rule id: {rule_id}")
        seen_ids.add(rule_id)

        if not isinstance(statement, str) or not statement:
            raise ValueError(f"rule[{index}] ({rule_id}) has invalid 'statement'")
        if not isinstance(owner_layer, str) or not owner_layer:
            raise ValueError(f"rule[{index}] ({rule_id}) has invalid 'owner_layer'")
        if not isinstance(requires_hardware, bool):
            raise ValueError(f"rule[{index}] ({rule_id}) has invalid 'requires_hardware'")
        if (
            not isinstance(tests, list)
            or not tests
            or not all(isinstance(node, str) and node for node in tests)
        ):
            raise ValueError(f"rule[{index}] ({rule_id}) must define non-empty string 'tests'")

        parsed.append(
            Rule(
                rule_id=rule_id,
                statement=statement,
                owner_layer=owner_layer,
                requires_hardware=requires_hardware,
                tests=tuple(tests),
            )
        )

    return parsed


def collect_node_exists(node: str) -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", node],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return True, ""
    error = (result.stderr or result.stdout).strip()
    return False, error or f"collect failed for {node}"


def check_rules(rules: list[Rule]) -> int:
    missing_nodes: list[tuple[str, str, str]] = []
    seen_nodes: set[str] = set()

    for rule in rules:
        if not rule.tests:
            missing_nodes.append((rule.rule_id, "<none>", "rule has no tests"))
            continue
        for node in rule.tests:
            if node in seen_nodes:
                continue
            seen_nodes.add(node)
            exists, error = collect_node_exists(node)
            if not exists:
                missing_nodes.append((rule.rule_id, node, error))

    if missing_nodes:
        print(
            f"Business-rule check failed: {len(missing_nodes)} invalid mapped test node(s):",
            file=sys.stderr,
        )
        for rule_id, node, error in missing_nodes:
            print(f"- {rule_id}: {node}", file=sys.stderr)
            print(f"  Error: {error}", file=sys.stderr)
        return 1

    print(
        "Business-rule check passed: "
        f"{len(rules)} rule(s), {len(seen_nodes)} mapped pytest node(s)."
    )
    return 0


def run_rule_tests(rules: list[Rule], *, fast: bool) -> int:
    selected_rules = [rule for rule in rules if (not fast or not rule.requires_hardware)]
    nodes = sorted({node for rule in selected_rules for node in rule.tests})
    if not nodes:
        print("No rule tests selected. Check catalog or --fast filter.", file=sys.stderr)
        return 2

    cmd = [sys.executable, "-m", "pytest"]
    if fast:
        cmd.extend(["-m", "not hardware"])
    cmd.extend(nodes)

    label = "fast" if fast else "full"
    print(f"Running {label} business-rule regression suite ({len(nodes)} test node(s))...")
    return subprocess.run(cmd, check=False).returncode


def main() -> int:
    args = parse_args()

    try:
        rules = load_rules(args.rules.resolve())
    except ValueError as exc:
        print(f"Business-rule configuration error: {exc}", file=sys.stderr)
        return 2

    if args.command == "check":
        return check_rules(rules)
    if args.command == "test":
        check_exit = check_rules(rules)
        if check_exit != 0:
            return check_exit
        return run_rule_tests(rules, fast=args.fast)

    print(f"Unknown command: {args.command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
