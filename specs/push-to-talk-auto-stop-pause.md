# Silicato Spec - Push-to-Talk Auto Stop on Long Pause

Status: Proposed
Created on: 2026-03-08

## Problem

Current push-to-talk requires a second Enter to stop recording.
For conversational usage, this adds friction and makes turns slower than needed.

## Goal

Keep push-to-start, but stop recording automatically after a configurable long pause in speech.

## Scope

1. Start capture with Enter as today.
2. Detect silence after speech has started and auto-stop recording when silence lasts long enough.
3. Keep manual Enter stop available as fallback.
4. Expose CLI configuration for silence auto-stop duration.
5. Update user-facing docs to describe the revised behavior.

## Non-goals

1. No always-on continuous listening mode.
2. No VAD model dependency additions.
3. No changes to transcription/send confirmation semantics.

## Acceptance Criteria

1. Default flow: Enter starts recording, long pause ends recording automatically.
2. Manual Enter stop still works during recording.
3. CLI documents how to tune/disable silence auto-stop.
4. Existing capture/transcribe/send behavior remains unchanged apart from stop trigger.
