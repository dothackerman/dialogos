# Application Layer

## Responsibility
- Implement use-cases that orchestrate a turn.
- Call domain logic and port interfaces.
- Coordinate workflow without concrete side effects.

## Allowed dependencies
- `dialogos.domain`
- `dialogos.ports`
- Side-effect-light stdlib helpers

## Forbidden dependencies
- `dialogos.adapters`
- `dialogos.ui`
- Direct subprocess/filesystem integrations for runtime behavior

## Expected test category
- `tests/unit` for use-case logic
- `tests/integration` with fake port implementations
