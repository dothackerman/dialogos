# Dialogos Agent Playbook

This file defines how agents collaborate in this repository.

## Roles
- Builder: implements code and tests from specs.
- Quality: validates maintainability, architecture boundaries, and gate checks.
- Docs: updates user-facing, agent-facing, and developer-only documentation.

## Required flow
1. Start from `specs/<feature>.md` (create/update first).
2. Builder implements.
3. Quality runs `make gate`.
4. Docs updates all impacted docs.
5. Merge only with quality signoff.

## Branch rules
- `feat/<slug>`
- `fix/<slug>`
- `docs/<slug>`
- `refactor/<slug>`
- `test/<slug>`
- `chore/<slug>`

## Commit rules
Use Conventional Commits only:
- `feat(scope): ...`
- `fix(scope): ...`
- `docs(scope): ...`
- `refactor(scope): ...`
- `test(scope): ...`
- `chore(scope): ...`

## Commands
- Install runtime deps: `make install`
- Install dev deps: `make install-dev`
- Install hooks: `make hooks`
- Quality checks: `make check`
- Full gate (blocking): `make gate`
