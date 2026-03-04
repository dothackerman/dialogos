# Capabilities

## MVP (current)
- Local push-to-talk speech capture
- Local transcription via Whisper (`faster-whisper`)
- German (`de`), English (`en`), and auto language detection
- Optional clipboard copy of transcript
- Optional transcript log append
- Runtime diagnostics (`--doctor`)

## In scope next
- tmux transport to send confirmed transcript directly to Codex
- Confirm-before-send as default interaction mode
- Activatable voice mode: auto-send transcript after user stops speaking

## Out of scope right now
- Cloud-only runtime dependencies
- Usage analytics/telemetry
- Spoken assistant replies (deferred milestone)
