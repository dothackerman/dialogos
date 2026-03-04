# Architecture

## Product name
Dialogos.

Intent: enable a natural communication channel between human speech and Codex text workflows.

## Tier-1 platform
- Ubuntu / TUXEDO OS

## Runtime posture
- Local-first and offline-capable after model download
- No usage telemetry
- Logs only for local debugging and agent workflows

## Module boundaries

### `src/dialogos/cli.py`
- CLI argument handling
- user prompts and interactive flow coordination

### `src/dialogos/contracts.py`
- typed contracts for adapters and data exchange
- stable boundaries for multi-agent parallel work

### `src/dialogos/orchestrator.py`
- orchestration logic independent from concrete adapters

### `src/dialogos/adapters/*`
- concrete implementations for transport/integration points
- examples: audio capture, STT backend, tmux sender

## Interaction milestones

1. Push-to-talk mode (MVP)
2. Activatable voice mode (auto-send after speech stop)
3. Spoken response output

## Language policy
- supported: `de`, `en`, `auto`
- Swiss-German handled via `de`/`auto` path (no dedicated `gsw` model code today)

## Quality gates
- formatter + lint + typing + tests in local gate
- integration and hardware tests are blocking
- branch and commit conventions enforced via git hooks
