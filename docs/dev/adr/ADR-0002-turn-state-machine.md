# ADR-0002: Turn State Machine

- Status: Accepted
- Date: 2026-03-04

## Context

Confirm flow (`send/edit/retry/skip/quit`) is central behavior and was previously spread across CLI branching paths, increasing regression risk.

## Decision

Model turn confirmation as an explicit state machine in domain/application logic:
- Parse user intent into canonical actions.
- Apply deterministic transitions.
- Keep CLI responsible for collecting input and rendering prompts only.

## Consequences

Positive:
- Behavior is testable without terminal I/O.
- Transition rules are explicit and reviewable.
- Preview and normal mode differences remain isolated.

Negative:
- Requires explicit transition modeling and maintenance.

## Alternatives considered

1. Keep ad-hoc branching in CLI.
- Rejected: difficult to validate for regressions.

2. Introduce external FSM framework.
- Rejected: unnecessary dependency for current complexity.
