# Ports Layer

## Responsibility
- Define typed contracts for external capabilities.
- Keep interfaces stable and implementation-agnostic.

## Allowed dependencies
- `typing`, `dataclasses`, and minimal shared value types.

## Forbidden dependencies
- `silicato.domain`
- `silicato.application`
- `silicato.adapters`
- `silicato.ui`
- Concrete runtime libraries (`tmux`, `faster-whisper`, ALSA wrappers)

## Expected test category
- `tests/contracts` validating adapter conformance.
