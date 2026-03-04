from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKER = PROJECT_ROOT / "scripts" / "check_architecture.py"
FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"


def run_checker(fixture_name: str) -> subprocess.CompletedProcess[str]:
    fixture_root = FIXTURES_ROOT / fixture_name
    rules_path = fixture_root / "architecture_rules.toml"
    return subprocess.run(
        [sys.executable, str(CHECKER), "--rules", str(rules_path)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_architecture_checker_accepts_allowed_imports() -> None:
    result = run_checker("pass")

    assert result.returncode == 0
    assert "Architecture check passed" in result.stdout
    assert result.stderr == ""


def test_architecture_checker_reports_forbidden_imports() -> None:
    result = run_checker("fail")

    assert result.returncode == 1
    assert "Architecture check failed" in result.stderr
    assert "src/dialogos/application/bad.py" in result.stderr
    assert "src/dialogos/domain/bad.py" in result.stderr
    assert "src/dialogos/ui/bad.py" in result.stderr
    assert "application -> adapters" in result.stderr
    assert "domain -> application" in result.stderr
    assert "ui -> domain" in result.stderr
    assert "Fix:" in result.stderr
