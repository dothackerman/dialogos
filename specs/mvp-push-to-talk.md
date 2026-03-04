# Spec: MVP Push-to-Talk (Milestone 1 Baseline)

## Objective
Allow a user on Ubuntu/TUXEDO Linux to speak, get local transcription (`de`/`en`/`auto`), confirm, and send text to a selected tmux pane running Codex.

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

## Non-functional requirements
- Works offline after model download.
- CPU-safe defaults.
- Clear terminal status messages.
- Deterministic error messages for missing tmux sessions/targets and mic/runtime failures.

## Acceptance criteria
- User can complete one full turn on Ubuntu/TUXEDO.
- Picker works for first-time tmux users.
- Remembered pane works and can be overridden.
- No tmux gives clear guided setup and exits non-zero.
- Preview mode enforces explicit send.
- JSONL logs are written with required fields.
- `make gate` passes on developer machine with real hardware available.

## Deferred beyond this spec
- Always-on voice mode with silence-based end detection.
- Spoken response output.
