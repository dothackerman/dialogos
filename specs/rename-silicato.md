# Silicato Rename and TestPyPI Redeploy

Status: Active
Date: 2026-03-06

## Goal

Rename project identity from `Dialogos`/`dialogos` to `Silicato`/`silicato` across package metadata, module paths, CLI entrypoints, docs, and release instructions; then publish the renamed package to TestPyPI.

## Scope

1. Packaging metadata:
- `pyproject.toml` project name, authors/maintainers text, URLs, console script.

2. Python package and imports:
- `src/dialogos` -> `src/silicato`.
- Internal imports and tests updated to `silicato.*`.
- Architecture checker defaults and fixture references updated.

3. User/developer docs:
- Project name references (`Dialogos`, `dialogos`) updated to `Silicato`, `silicato`.
- Command examples updated from `dialogos` CLI to `silicato` CLI.
- Env vars and state/config paths updated from `DIALOGOS_*` and `.../dialogos/...` to `SILICATO_*` and `.../silicato/...`.

4. Repository identity:
- Local folder renamed from `dialogos` to `silicato`.
- GitHub repository renamed from `dothackerman/dialogos` to `dothackerman/silicato`.
- Remote URL updated to new repo.

5. Release operation:
- Build artifacts for renamed package.
- Upload to TestPyPI using configured `TEST_PYPI_TOKEN`.

## Constraints

- Keep runtime behavior unchanged except naming.
- Do not fix the known parallel tmux target collision in this scope.
- Preserve architecture layering and business-rule mapping integrity.

## Acceptance Criteria

1. `python -m silicato --help` resolves.
2. `silicato --help` entrypoint resolves from package metadata.
3. `make test-arch` and `make test-rules-fast` pass after rename.
4. TestPyPI upload succeeds for `silicato` package.
5. GitHub remote points to `dothackerman/silicato`.
