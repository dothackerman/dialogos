# Silicato Milestone 4 - Single-Enter Capture Stop

## Summary
This milestone removes the need to press Enter a second time to end recording.

Current baseline is push-to-talk with Enter start and Enter stop.  
Target behavior is Enter to start, then automatic stop without second Enter.

## Why this milestone exists
Current turn completion friction is high because users must perform two explicit keyboard actions per turn.

Reducing stop friction should improve usability without changing core tmux, preview, or logging behavior.

## Relationship to prior specs
1. Builds on `specs/mvp-push-to-talk.md`.
2. Changes the capture-stop interaction from the MVP baseline.
3. Keeps architecture boundaries from `specs/milestone-2-architecture.md` and hardening from `specs/milestone-3-agent-first-hardening.md`.

## Objectives
1. Keep Enter-to-start turn behavior.
2. Remove Enter-to-stop dependency.
3. End turns automatically with predictable, bounded latency.
4. Preserve existing confirm flow and tmux send semantics.
5. Keep implementation within current layer boundaries.

## Non-goals
1. No always-on listening mode.
2. No wake-word detection.
3. No spoken output (TTS).
4. No cloud-side audio processing.
5. No redesign of preview actions (`send/edit/retry/skip/quit`).

## Decision framing from discovery
1. Easy path: fixed max duration auto-stop only.
2. Recommended path: silence-based auto-stop with max-duration fallback.
3. Hard path: highly adaptive silence detection for noisy and varied microphones.

## Recommended product behavior
1. User presses Enter once to begin capture.
2. Capture stops automatically after trailing silence threshold is reached.
3. Hard max duration ends capture if silence threshold is never reached.
4. Ctrl+C during recording remains a safe escape path.
5. Existing transcription, confirmation, sending, and logging continue unchanged.

## Scope

### In scope
1. Replace second-Enter stop mechanism with automatic stop logic.
2. Update CLI prompt text and user docs to match new interaction.
3. Add regression tests for stop behavior decision points.
4. Add business-rule catalog entry for single-enter stop behavior.

### Out of scope
1. Continuous background listening.
2. Device-specific per-microphone calibration workflows.
3. New UI surfaces beyond current CLI.

## Architecture constraints
1. `ui` remains responsible for prompt text and composition only.
2. Stop-condition orchestration belongs in application and/or adapter boundaries, not domain.
3. Domain remains side-effect free.
4. Application does not import adapters directly.

## Proposed execution phases

### Phase 0 - Baseline lock
1. Keep current behavior tests green before changes.
2. Add characterization test coverage around capture-stop flow boundaries with fakes where possible.

### Phase 1 - Auto-stop MVP
1. Implement automatic stop without second Enter.
2. Ensure max-duration fallback exists to prevent hanging recordings.
3. Keep user-facing logs/messages clear when max duration triggers.

### Phase 2 - Tuning and hardening
1. Tune default silence and max-duration thresholds.
2. Validate behavior on supported Linux baseline with real microphone input.
3. Stabilize failure-path messaging.

## Acceptance criteria
1. In normal interactive flow, user starts recording with one Enter and never needs a second Enter to finish.
2. Recording ends automatically after speech ends in typical quiet-room usage.
3. If silence is not detected, recording still ends at deterministic max duration.
4. Empty-transcript handling remains unchanged (skip semantics).
5. Preview flow behavior remains unchanged.
6. Existing tmux send behavior remains unchanged.
7. Architecture checks and fast business-rule regressions pass.

## Risks and tradeoffs
1. Risk: noisy environments may delay silence detection.
2. Risk: aggressive silence threshold may truncate speech.
3. Tradeoff: lower latency stop can increase false end-of-turn cuts.
4. Tradeoff: conservative thresholds reduce truncation but keep turns open longer.

## Failure modes to guard explicitly
1. Capture never stops due to persistent ambient noise.
2. Short natural pauses inside one sentence split the utterance too early.
3. Exit/error handling regresses when stop event comes from auto-detection instead of keyboard input.

## Test strategy
1. Unit tests for stop-decision logic (silence reached, max duration reached, manual interruption).
2. Integration tests with fake capture adapter to assert orchestration does not require second Enter.
3. Hardware smoke validation on supported platform with real mic and tmux.

## Documentation impact
1. Update `README.md` capability wording from Enter start/stop to single Enter + auto-stop.
2. Update `docs/user/capabilities.md` and `docs/user/quickstart.md`.
3. Keep `specs/mvp-push-to-talk.md` unchanged as historical baseline.
4. Record new behavior in current docs and business-rule catalog.

## Candidate rule additions
1. Add new business-rule ID for single-enter automatic stop behavior.
2. Map it to unit/integration regressions and hardware coverage where applicable.

## Open decisions for kickoff
1. Default stop strategy for first release of this milestone: fixed duration only, or silence + max-duration fallback.
2. Whether to expose stop thresholds as CLI flags in milestone scope or keep internal defaults initially.

## Definition of done
Milestone 4 is complete when:
1. Single-enter interaction is the default capture flow.
2. Automatic stop is reliable within documented constraints.
3. Tests and rule mappings cover the new behavior.
4. User and developer docs reflect current behavior accurately.
