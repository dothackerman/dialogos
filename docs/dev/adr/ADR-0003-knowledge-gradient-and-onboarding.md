# ADR-0003: Knowledge Gradient and Onboarding

- Status: Accepted
- Date: 2026-03-04

## Context

New sessions were slowed by broad mandatory reading and repeated context loading. This reduced throughput for scoped tasks.

## Decision

Adopt a knowledge gradient:
- Bootstrap pack (mandatory):
  - `AGENTS.md`
  - `docs/dev/patterns-quickstart.md`
  - `docs/dev/dependency-rules.md`
  - `docs/agents/new-session-handoff.md`
- On-demand pack (task-driven):
  - `docs/dev/patterns-deep-dive.md`
  - `docs/dev/adr/*`
  - touched layer README(s)

Session leaders should avoid requiring deep-dive docs when bootstrap plus local layer docs are sufficient.

## Consequences

Positive:
- Faster startup for scoped work.
- Better context hygiene across parallel agents.

Negative:
- Requires discipline to keep bootstrap docs concise and accurate.

## Alternatives considered

1. Full mandatory reading for every session.
- Rejected: high overhead and low marginal value.

2. No standard onboarding pack.
- Rejected: inconsistent decisions and repeated mistakes.
