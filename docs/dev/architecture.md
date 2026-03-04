# Architecture

## Product name
Dialogos.

Intent: enable a local-first communication channel between human speech and Codex text workflows.

## Runtime posture
- Local-first and offline-capable after model download
- No telemetry
- Local JSONL turn logs only
- Milestone 3 hardening is behavior-preserving for Milestone 1 user flow

## Layered architecture target

### `src/dialogos/domain/`
- Pure business state and transitions (no side effects)
- Owns turn state machine and confirm action semantics
- No filesystem/subprocess/env/terminal/network imports

### `src/dialogos/application/`
- Use-case orchestration for turn flow
- Coordinates domain decisions and port calls
- May import `domain` and `ports`, never adapters

### `src/dialogos/ports/`
- Typed interfaces for external capabilities
- Examples: audio capture, STT, sender, target resolver, config store, turn logger

### `src/dialogos/adapters/`
- Concrete side-effect implementations (tmux, ALSA, whisper, storage)
- Implements `ports` contracts

### `src/dialogos/ui/`
- CLI argument parsing, prompts, output rendering, and dependency wiring
- Entry points stay `dialogos` and `python3 -m dialogos`
- May compose adapters and call application use-cases

## Dependency direction (strict)

Allowed:
- `ui -> application`
- `application -> domain`
- `application -> ports`
- `adapters -> ports`
- `ui -> adapters` for composition only

Forbidden:
- `domain -> application|ui|adapters|ports`
- `application -> adapters|ui`
- `adapters -> application|domain|ui`
- `ui -> domain`

## Turn behavior (unchanged)
1. Resolve tmux target (`--tmux-target` -> `DIALOGOS_TMUX_TARGET` -> remembered target -> picker)
2. Validate target
3. Capture push-to-talk audio
4. Transcribe locally
5. Confirm action (`send/edit/retry/skip/quit`)
6. Send to tmux when confirmed
7. Append JSONL turn log event

## Quality and enforcement
- Use `make test-arch` for architecture boundary checks
- Use `make check-rules` to validate business-rule to regression-test mappings
- Use `make test-rules-fast` for non-hardware business-rule regressions
- Use `make test-rules` for full business-rule regressions (includes hardware)
- `make gate` remains the blocking local gate
- Architecture and rule checks are expected to run inside `make check`/`make gate`

## Testing taxonomy target
- `tests/unit`: pure logic and helpers
- `tests/contracts`: adapter compliance with port contracts
- `tests/integration`: multi-component behavior with fakes/stubs where possible
- `tests/hardware`: local runtime checks (tmux/ALSA)

## Knowledge gradient entrypoints
- Bootstrap: `docs/dev/patterns-quickstart.md`, `docs/dev/dependency-rules.md`
- Deep dive: `docs/dev/patterns-deep-dive.md`, `docs/dev/adr/*`
