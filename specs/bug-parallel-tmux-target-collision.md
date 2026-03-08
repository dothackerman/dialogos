# Silicato Bug Report - Parallel tmux Target Collision

Status: Closed (no longer reproducible in current usage)
Reported on: 2026-03-06
Closed on: 2026-03-08

## Summary

When two Silicato processes run at the same time with different tmux targets, both prompts can be sent to the same pane instead of each process using its own target.

## Observed Behavior

- Instance A targets pane `...0.2`.
- Instance B targets pane `...0.0`.
- Prompts from both instances are delivered to pane `...0.2`.

## Expected Behavior

Each running Silicato process should remain isolated to its own resolved target for the full turn lifecycle.

## Reproduction (as reported)

1. Start two Silicato instances in parallel.
2. Configure different tmux pane targets for each instance.
3. Send turns from both instances.
4. Observe that both turns land in pane `...0.2` instead of separate panes.

## Constraints

- Do not address this bug during the rename/release-name migration work.
- Preserve current single-instance behavior while implementing any future fix.

## Failure Modes To Investigate

- Shared target persistence may be overwritten while concurrent processes run.
- Target resolution order may unintentionally reuse a recently persisted target.
- Sender wiring may ignore per-process resolved target under concurrent execution.

## Fix Acceptance Criteria (future)

1. Two parallel processes with explicit, different `--tmux-target` values send to their own panes.
2. A regression test covers concurrent target isolation.
3. Existing target precedence behavior remains unchanged for single-process usage.
