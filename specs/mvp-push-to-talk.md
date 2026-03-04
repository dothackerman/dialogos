# Spec: MVP Push-to-Talk (Behavior Baseline)

## Objective
Allow a user on Ubuntu/TUXEDO Linux to speak, get local transcription (`de`/`en`/`auto`), confirm, and send text to a selected tmux pane running Codex.

Milestone 2 keeps this behavior unchanged while migrating implementation to layered architecture with enforceable boundaries.

## Functional requirements
- Push-to-talk interaction via Enter start/stop.
- Local STT with Whisper (`faster-whisper`).
- Language options: `de`, `en`, `auto` (default `auto`).
- tmux mandatory send transport.
- Target resolution order:
  1. `--tmux-target`
  2. `DIALOGOS_TMUX_TARGET`
  3. remembered config target
  4. interactive picker
- First-time indexed tmux picker (no tmux syntax required).
- Remember selected target by default (with opt-out flag).
- Confirm flow:
  - Normal mode: `Enter=send`, `e=edit`, `r=retry`, `s=skip`, `q=quit`
  - Preview mode: explicit send only.
- JSONL turn log append on local disk.
- Diagnostics command (`--doctor`).

## Architecture constraints (Milestone 2 target)
- Layer direction stays strict: `ui -> application -> domain`, `application -> ports`, `adapters -> ports`.
- Domain logic is side-effect free.
- UI handles parsing/prompts/wiring and delegates behavior to use-cases.
- Architecture boundary checks are part of local gate (`make test-arch`, `make gate`).

## Non-functional requirements
- Works offline after model download.
- CPU-safe defaults.
- Clear terminal status messages.
- Deterministic error messages for missing tmux sessions/targets and mic/runtime failures.
- Architecture boundaries are automatically enforced in developer workflow.

## Acceptance criteria
- User can complete one full turn on Ubuntu/TUXEDO.
- Picker works for first-time tmux users.
- Remembered pane works and can be overridden.
- No tmux gives clear guided setup and exits non-zero.
- Preview mode enforces explicit send.
- JSONL logs are written with required fields.
- Entry points stay `dialogos` and `python3 -m dialogos`.
- Architecture checks fail on boundary violations.
- `make gate` passes on developer machine with real hardware available.

## Deferred beyond this spec
- Always-on voice mode with silence-based end detection.
- Spoken response output.
