# Agent Roles

Dialogos uses a 3-role multi-agent model.

## 1) Builder Agent
- Implements feature code and tests from spec.
- Keeps module boundaries aligned with architecture docs.
- Must update or add tests for every behavior change.

## 2) Quality Agent
- Reviews maintainability, correctness, and agent legibility.
- Enforces formatting, linting, typing, and integration tests.
- Blocks merge if architecture boundaries are violated.

## 3) Docs Agent
- Updates user-facing docs for behavior/dependency changes.
- Updates agent-facing docs for workflow/process changes.
- Maintains developer-only deferred ideas and architecture notes.

## Merge policy
- `main` requires quality signoff.
- Docs signoff is required when user-facing behavior, dependencies, or setup changes.
