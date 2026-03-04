# Adapters Layer

## Responsibility
- Implement side-effectful integrations (tmux, audio capture, speech-to-text, storage).
- Satisfy interfaces declared in `dialogos.ports`.

## Allowed dependencies
- `dialogos.ports`
- Runtime libraries and system integrations
- stdlib modules needed for I/O

## Forbidden dependencies
- `dialogos.domain`
- `dialogos.application`
- `dialogos.ui`

## Expected test category
- `tests/contracts` for contract compliance
- `tests/integration` for behavior with fakes/stubs
- `tests/hardware` for local runtime checks where needed
