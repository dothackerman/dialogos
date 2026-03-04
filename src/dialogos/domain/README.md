# Domain Layer

## Responsibility
- Own pure business behavior and state transitions.
- Define canonical turn actions and transition rules.

## Allowed dependencies
- Python stdlib modules that are side-effect free (`dataclasses`, `typing`, `enum`, etc.).
- Internal domain modules only.

## Forbidden dependencies
- `dialogos.application`
- `dialogos.ports`
- `dialogos.adapters`
- `dialogos.ui`
- Side-effect APIs (`subprocess`, filesystem/network/terminal I/O)

## Expected test category
- `tests/unit` with deterministic pure-logic cases.
