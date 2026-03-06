# UI Layer

## Responsibility
- Parse CLI args and render prompts/messages.
- Compose adapters and inject them into application use-cases.
- Keep user interaction concerns separate from core behavior.

## Allowed dependencies
- `silicato.application`
- `silicato.ports`
- `silicato.adapters` (composition/wiring)

## Forbidden dependencies
- `silicato.domain`
- Direct business-rule branching that bypasses application use-cases.
- Adapter-specific behavior embedded as policy decisions.

## Expected test category
- `tests/unit` for argument parsing and prompt helpers
- `tests/integration` for end-to-end CLI flow with fakes
