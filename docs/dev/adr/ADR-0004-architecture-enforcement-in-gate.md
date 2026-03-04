# ADR-0004: Architecture Enforcement in Gate

- Status: Accepted
- Date: 2026-03-04

## Context

Boundary rules documented in prose alone do not prevent regressions under parallel development.

## Decision

Make architecture checks blocking in local quality flow:
- Provide explicit architecture check command: `make test-arch`.
- Integrate architecture checks into `make check` and `make gate`.
- Treat violations as gate failures.

## Consequences

Positive:
- Objective and repeatable boundary enforcement.
- Faster reviews due to automated import validation.

Negative:
- Rules and checker require maintenance when package layout evolves.
- False positives may require targeted rule refinement.

## Alternatives considered

1. Manual code review only.
- Rejected: inconsistent and not scalable.

2. Non-blocking warning-only check.
- Rejected: insufficient to prevent drift.
