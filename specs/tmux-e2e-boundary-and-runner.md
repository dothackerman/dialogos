# Silicato Spec - tmux E2E Boundary and Runner

Status: Implemented
Created on: 2026-03-06

## Problem

tmux interactions are scattered across runtime adapters and hardware smoke tests.
This makes tmux-related regressions harder to reproduce consistently and encourages ad-hoc command execution paths.

## Goal

Introduce a single tmux runtime boundary used by tmux adapters and tmux hardware smoke tests, plus one stable make target for tmux E2E smoke execution.

## Scope

1. Add a shared tmux runtime adapter in `src/silicato/adapters/tmux/`.
2. Route `TmuxSender` and `TmuxTargetResolver` through that adapter.
3. Route tmux hardware smoke test interactions through the same adapter.
4. Add a dedicated `make test-e2e-tmux` command for tmux smoke execution.
5. Keep behavior and public CLI flags unchanged.

## Non-Goals

1. No redesign of transcription or confirmation flows.
2. No change to target precedence policy.
3. No containerization changes in this scope.

## Acceptance Criteria

1. All runtime tmux commands in touched paths are executed through the shared tmux runtime adapter.
2. Existing sender and resolver contract tests remain green.
3. Hardware tmux smoke test still validates create/send/capture/cleanup flow.
4. `make test-e2e-tmux` runs only tmux hardware smoke checks.
