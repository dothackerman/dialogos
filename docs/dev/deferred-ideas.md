# Deferred Ideas (Developer-only)

This file intentionally stores ideas that are deferred to keep iteration fast.

## Product and UX
- Activatable voice mode with silence-end auto-send
- Interrupt command while assistant speaks
- Command mode vs chat mode prefixes
- Confidence-based confirm behavior tuning

## Audio backends
- PipeWire-native capture adapter in addition to ALSA
- Device auto-selection heuristics
- Per-mic calibration profile

## STT quality
- Phrasebook benchmarking for DE/EN
- Domain vocabulary injection and normalization rules
- Swiss-German post-processing experiments

## tmux/Codex integration
- Reply scraping robustness across terminal layouts
- Turn-level timeout policy
- Session auto-discovery of target pane

## TTS milestone
- Local `piper` adapter
- Voice profile mapping by language
- Chunked streaming playback

## Observability (local only)
- Structured local logs with turn IDs
- Failure taxonomy and fast triage report command

## Packaging and distribution
- Debian package path
- `pipx` install path
- signed release artifacts once product confidence is high
