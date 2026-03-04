# Architecture

## Product name
Dialogos.

Intent: enable a local-first communication channel between human speech and Codex text workflows.

## Tier-1 platform
- Ubuntu / TUXEDO OS

## Runtime posture
- Local-first and offline-capable after model download
- No telemetry
- Local JSONL turn logs only

## Module boundaries

### `src/dialogos/cli.py`
- CLI argument handling
- startup target resolution
- confirm loop and user prompts

### `src/dialogos/contracts.py`
- typed contracts for adapters and data exchange

### `src/dialogos/orchestrator.py`
- capture/transcribe/send orchestration
- confirm action parsing helpers

### `src/dialogos/tmux_picker.py`
- tmux pane listing
- interactive index-based picker
- target validation and no-session guidance

### `src/dialogos/config.py`
- load/save remembered `tmux_target`
- XDG config path resolution

### `src/dialogos/logging_jsonl.py`
- JSONL log schema and append
- XDG state path resolution

### `src/dialogos/adapters/tmux_sender.py`
- concrete tmux `send-keys` transport adapter

## Milestone 1 flow
1. Resolve tmux target (`--tmux-target` -> `DIALOGOS_TMUX_TARGET` -> remembered -> picker)
2. Validate target
3. Capture push-to-talk audio
4. Transcribe locally
5. Confirm action (`send/edit/retry/skip/quit`)
6. Send to tmux when confirmed
7. Append JSONL log event

## Language policy
- supported: `de`, `en`, `auto`

## Quality gates
- formatter + lint + typing + tests in local gate
- hardware tests are blocking in `make gate`
- branch and commit conventions enforced via git hooks
