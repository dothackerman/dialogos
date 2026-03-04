# Ports Layer

## Responsibility
- Define typed contracts for external capabilities.
- Keep interfaces stable and implementation-agnostic.

## Allowed dependencies
- `typing`, `dataclasses`, and minimal shared value types.

## Forbidden dependencies
- `dialogos.domain`
- `dialogos.application`
- `dialogos.adapters`
- `dialogos.ui`
- Concrete runtime libraries (`tmux`, `faster-whisper`, ALSA wrappers)

## Expected test category
- `tests/contracts` validating adapter conformance.
