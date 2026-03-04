#!/usr/bin/env python3
"""Backward-compatible entrypoint for the Dialogos CLI."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))

    from dialogos.cli import main as dialogos_main

    return dialogos_main()


if __name__ == "__main__":
    raise SystemExit(main())
