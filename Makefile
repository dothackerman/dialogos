.PHONY: install install-dev hooks format lint typecheck check test test-fast gate

VENV_PYTHON := .venv/bin/python3

ifeq ($(wildcard $(VENV_PYTHON)),)
PYTHON := python3
else
PYTHON := $(VENV_PYTHON)
endif

install:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e .[dev]

hooks:
	chmod +x .githooks/commit-msg .githooks/pre-push scripts/validate_branch_name.sh
	git config core.hooksPath .githooks

format:
	$(PYTHON) -m ruff format .

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy src tests talk_to_codex.py

check: format lint typecheck

test:
	$(PYTHON) -m pytest

test-fast:
	$(PYTHON) -m pytest -m "not hardware"

gate: check test-fast test
