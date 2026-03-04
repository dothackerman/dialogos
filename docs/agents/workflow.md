# Agent Workflow

## Branch naming

Allowed branch patterns:
- `feat/<slug>`
- `fix/<slug>`
- `docs/<slug>`
- `refactor/<slug>`
- `test/<slug>`
- `chore/<slug>`
- `main` (protected target branch)

## Commit message format

Conventional commits are mandatory:
- `feat(scope): summary`
- `fix(scope): summary`
- `docs(scope): summary`
- `refactor(scope): summary`
- `test(scope): summary`
- `chore(scope): summary`

## Required local gate

Before pushing:

```bash
make gate
```

`make gate` includes:
- formatter
- lint checks
- type checks
- unit tests
- integration tests
- hardware-dependent tests

If hardware tests fail, the gate fails.

## Workflow per feature

1. Create or update `specs/<feature>.md`.
2. Builder agent implements code + tests.
3. Quality agent runs `make gate` and reviews architecture fit.
4. Docs agent updates affected docs.
5. Merge only after required signoffs.
