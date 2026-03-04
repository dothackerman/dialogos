# ADR-0001: Layered Hexagonal Boundaries

- Status: Accepted
- Date: 2026-03-04

## Context

Milestone 1 concentrated behavior in CLI-heavy modules, creating merge hotspots and weak boundaries between business logic and side effects.

## Decision

Adopt a layered hexagonal structure:
- `domain`: pure behavior/state transitions
- `application`: use-case orchestration
- `ports`: capability interfaces
- `adapters`: side-effect implementations
- `ui`: CLI arguments, prompts, and wiring

Dependency direction is strict:
- `ui -> application -> domain`
- `application -> ports`
- `adapters -> ports`

## Consequences

Positive:
- Parallel agent work with fewer conflicts.
- Deterministic unit tests for domain/application behavior.
- Easier adapter replacement.

Negative:
- Additional boilerplate and wiring.
- More files to navigate.

## Alternatives considered

1. Keep Milestone 1 structure and rely on review discipline only.
- Rejected: boundaries continue to erode.

2. Full plugin/event architecture.
- Rejected: too complex for current scope.
