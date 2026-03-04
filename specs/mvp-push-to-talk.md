# Spec: MVP Push-to-Talk

## Objective
Allow a user on Ubuntu/TUXEDO Linux to speak, get local transcription (DE/EN/auto), confirm, and send text to Codex.

## Functional requirements
- Push-to-talk interaction via Enter start/stop.
- Local STT with Whisper (`faster-whisper`).
- Language options: `de`, `en`, `auto` (default `auto`).
- Confirm-before-send default behavior.
- Optional clipboard copy.
- Basic diagnostics command.

## Non-functional requirements
- Works offline after model download.
- CPU-safe defaults.
- Clear terminal status messages.
- Deterministic error messages for common mic/runtime failures.

## Acceptance criteria
- User can complete one full turn on Ubuntu/TUXEDO.
- Transcript output is non-empty for a clear spoken sentence.
- Confirm flow blocks send when declined.
- `make gate` passes on developer machine.

## Deferred from MVP
- Always-on voice mode with silence-based end detection.
- Spoken response output.
