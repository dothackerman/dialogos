# Feature Request: Single-Enter Auto-Stop Capture

Date: 2026-03-10
Status: Proposed
Owner: OG (requested), Sil (drafted)
Source: `feat/milestone-feature-planning`

## Summary

Reduce capture friction by changing the recording interaction from:

- Enter to start
- Enter to stop

to:

- Enter to start
- Automatic stop after speech ends

## Problem

Current turn completion requires a second explicit keyboard action to stop recording.

Pain points:
- Extra friction on every turn
- Slower operator flow in rapid back-and-forth usage
- Higher chance of awkward pauses while managing tmux-based workflows

## Proposed Solution

Replace the second-Enter stop interaction with automatic stop behavior.

Recommended MVP:
- Start recording with one Enter
- Stop after trailing silence is detected
- Fall back to a hard max duration if silence is never detected
- Preserve current transcription, preview, confirm, logging, and tmux send flow

## UX / Safety Rules

1. Users should never need a second Enter to finish a normal turn.
2. Auto-stop must have deterministic max-duration fallback to avoid hanging capture.
3. Ctrl+C during recording remains a safe escape path.
4. Empty-transcript handling should remain unchanged.
5. If max-duration fallback triggers, the CLI should explain why capture stopped.

## Constraints

1. Keep architecture boundaries intact: UI for prompts/composition, application for orchestration, domain pure.
2. Do not regress existing preview actions (`send/edit/retry/skip/quit`).
3. Do not change tmux send semantics.
4. Avoid adding continuous listening, wake-word behavior, or cloud-side audio processing in MVP.

## Tradeoffs and Failure Modes

Tradeoffs:
- Faster stop thresholds improve responsiveness but increase truncation risk.
- More conservative thresholds reduce truncation risk but keep turns open longer.

Failure modes to guard against:
- Ambient noise prevents silence detection, so recording must stop at max duration.
- Natural pauses inside a sentence trigger stop too early.
- Auto-stop event handling regresses exit/error paths that previously depended on manual stop.

## Acceptance Criteria

1. User starts recording with one Enter and does not need a second Enter to stop.
2. Recording ends automatically after speech ends in typical quiet-room use.
3. If silence is not detected, recording still ends at a deterministic max duration.
4. Existing preview and send behavior remains unchanged.
5. Regression coverage exists for silence stop, max-duration stop, and interruption behavior.

## Suggested Follow-Up

1. If prioritized, create a fresh implementation spec rather than reviving the old branch.
2. Validate the first version with fixed defaults before exposing threshold tuning to CLI flags.

## Why This Matters

This removes a repetitive interaction tax from every turn while staying aligned with the current terminal-first workflow.
