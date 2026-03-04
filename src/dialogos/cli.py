"""Compatibility CLI shim for the layered runtime."""

from .ui.cli.main import main

if __name__ == "__main__":
    raise SystemExit(main())
