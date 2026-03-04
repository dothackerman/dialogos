# Dialogos Milestone 2 - Architecture, Knowledge Gradient, and Enforcement

## Summary
Milestone 2 establishes an architecture that makes parallel subagent execution the default rational choice without policy coercion.

This milestone introduces:
1. Layered boundaries (domain, application, ports, adapters, UI).
2. A YAGNI knowledge gradient for new sessions (must-know now vs read when needed).
3. Automated architecture enforcement in the local gate.
4. Contract and integration testing aligned to ports/layers.

The result should be that agents naturally pick independent slices with minimal merge overlap.

## Why this milestone exists
Current friction is concentrated in `src/dialogos/cli.py` as a behavioral bottleneck. Multiple concerns are coupled in one place:
- input/output prompts
- target resolution policy
- runtime checks and fallback logic
- confirm flow transitions
- logging decisions

This makes subagent parallelism fragile because unrelated changes collide in shared code.

## Objectives
1. Refactor code into stable architecture seams that map cleanly to agent ownership.
2. Make new-session onboarding self-explanatory with minimal mandatory reading.
3. Enforce dependency boundaries automatically (`make gate`) to prevent regression.
4. Keep behavior from Milestone 1 unchanged during architecture migration.

## Non-goals
1. No new product features beyond architecture/maintainability.
2. No redesign of current tmux/audio behavior.
3. No replacement of existing test frameworks.
4. No cloud CI requirement in this milestone.

## Success criteria
1. At least 80 percent of architecture changes can be done in parallel with no shared-file conflicts in `ui/cli`.
2. `make gate` fails on architecture rule violations.
3. New agent startup requires only the bootstrap pack docs and can complete a scoped task without reading deep-dive docs.
4. Milestone 1 runtime behavior remains unchanged and all tests pass.

## Target architecture

### Layer map
1. `src/dialogos/domain/`
- Pure business state and transitions.
- No subprocess/filesystem/env/terminal I/O.

2. `src/dialogos/application/use_cases/`
- Orchestrates domain decisions and port calls.
- No concrete adapter imports.

3. `src/dialogos/ports/`
- Typed interfaces for external capabilities.
- Examples: `AudioCapture`, `SpeechToText`, `Sender`, `TargetResolver`, `ConfigStore`, `TurnLogger`.

4. `src/dialogos/adapters/`
- Concrete implementations.
- `tmux`, `alsa`, `whisper`, `storage` implementations live here.

5. `src/dialogos/ui/cli/`
- Argument parsing, prompt rendering, and dependency wiring only.
- Delegates behavior to use-cases.

### Dependency direction (strict)
Allowed direction only:
- `ui -> application -> domain`
- `application -> ports`
- `adapters -> ports`
- `ui` may compose adapters and pass them to application

Forbidden:
- `domain -> application|ui|adapters`
- `application -> adapters`
- `ui -> domain internals that bypass use-cases`

## YAGNI knowledge gradient

### Mandatory bootstrap pack (all new agents)
1. `AGENTS.md`
2. `docs/dev/patterns-quickstart.md`
3. `docs/dev/dependency-rules.md`
4. `docs/agents/new-session-handoff.md`

Expected reading time target: 10-15 minutes.

### On-demand pack (read only if task requires it)
1. `docs/dev/adr/*`
2. `docs/dev/patterns-deep-dive.md`
3. `src/dialogos/<layer>/README.md` for touched layer only
4. Adapter-specific runbooks for touched adapter only

### Rule for session leaders
Do not require deep-dive documents for tasks that can be completed from bootstrap + local layer README.

## Deliverables and file-by-file plan

### Workstream A - Documentation foundation
Create/update:
1. `docs/dev/patterns-quickstart.md`
- One-page architecture map
- 5 core rules
- "If you only remember three things" section

2. `docs/dev/dependency-rules.md`
- Allowed import matrix
- Forbidden examples
- Review checklist for PRs/agents

3. `docs/dev/patterns-deep-dive.md`
- Rationale and tradeoffs for each chosen pattern
- When not to use each pattern

4. `docs/dev/adr/README.md`
- ADR naming format and lifecycle

5. `docs/dev/adr/ADR-0001-layered-hexagonal-boundaries.md`
6. `docs/dev/adr/ADR-0002-turn-state-machine.md`
7. `docs/dev/adr/ADR-0003-knowledge-gradient-and-onboarding.md`
8. `docs/dev/adr/ADR-0004-architecture-enforcement-in-gate.md`

9. `src/dialogos/domain/README.md`
10. `src/dialogos/application/README.md`
11. `src/dialogos/ports/README.md`
12. `src/dialogos/adapters/README.md`
13. `src/dialogos/ui/README.md`
- Each README must include:
  - responsibility
  - allowed dependencies
  - forbidden dependencies
  - expected test category

14. `docs/agents/new-session-handoff.md`
- Add bootstrap pack and on-demand pack sections

15. `AGENTS.md`
- Keep concise, reference bootstrap docs, and avoid duplicating deep content

### Workstream B - Codebase restructuring (behavior-preserving)
Create/move:
1. `src/dialogos/ui/cli/main.py`
2. `src/dialogos/ui/cli/args.py`
3. `src/dialogos/ui/cli/prompts.py`
4. `src/dialogos/ui/cli/runtime_checks.py`

5. `src/dialogos/application/use_cases/resolve_target.py`
6. `src/dialogos/application/use_cases/run_capture_transcribe.py`
7. `src/dialogos/application/use_cases/confirm_turn.py`
8. `src/dialogos/application/use_cases/send_turn.py`
9. `src/dialogos/application/use_cases/log_turn.py`

10. `src/dialogos/domain/turn_state.py`
11. `src/dialogos/domain/confirm_actions.py`

12. `src/dialogos/ports/audio.py`
13. `src/dialogos/ports/stt.py`
14. `src/dialogos/ports/sender.py`
15. `src/dialogos/ports/targeting.py`
16. `src/dialogos/ports/storage.py`

17. `src/dialogos/adapters/tmux/target_resolver.py`
18. `src/dialogos/adapters/tmux/sender.py`
19. `src/dialogos/adapters/audio/alsa_capture.py`
20. `src/dialogos/adapters/stt/whisper.py`
21. `src/dialogos/adapters/storage/config_store.py`
22. `src/dialogos/adapters/storage/jsonl_turn_logger.py`

Compatibility handling:
23. Keep `src/dialogos/cli.py` as temporary thin compatibility shim importing `ui/cli/main.py`.
24. Keep `src/dialogos/__main__.py` unchanged in behavior.

### Workstream C - Architecture enforcement
Create/update:
1. `architecture_rules.toml`
- Define import boundaries by module prefix.

2. `scripts/check_architecture.py`
- Parse project Python files.
- Validate imports against rules.
- Exit non-zero with actionable violations.

3. `tests/architecture/test_architecture_rules.py`
- Verifies checker catches deliberate invalid examples.

4. `Makefile`
- Add `test-arch` target.
- Add `test-arch` into `check` and `gate`.

### Workstream D - Test taxonomy alignment
Create/update:
1. `tests/contracts/`
- `test_sender_contract.py`
- `test_target_resolver_contract.py`
- `test_config_store_contract.py`
- `test_turn_logger_contract.py`

2. `tests/integration/`
- Keep end-to-end behavior tests.
- Update imports for refactored structure.

3. `tests/hardware/`
- Move hardware checks out of integration namespace.
- Preserve current tmux/ALSA coverage.

4. `pyproject.toml`
- Keep pytest markers accurate for new test layout.

### Workstream E - Docs and spec alignment
Create/update:
1. `README.md` architecture section
2. `docs/dev/architecture.md`
3. `docs/agents/workflow.md`
4. `specs/mvp-push-to-talk.md`

## Execution phases

### Phase 0 - Baseline lock
1. Capture current behavior with characterization tests.
2. Confirm `make gate` passes before architecture edits.

Exit criteria:
- Baseline tag/commit created.
- Characterization tests merged.

### Phase 1 - Knowledge layer
1. Add bootstrap and on-demand documentation.
2. Add layer READMEs and ADRs.

Exit criteria:
- New agent can identify where to implement a task in under 5 minutes.

### Phase 2 - Enforcement layer
1. Implement architecture checker.
2. Wire checker into `make check` and `make gate`.

Exit criteria:
- Intentional boundary violation fails local gate.

### Phase 3 - Structural refactor
1. Extract CLI responsibilities into UI/application/domain/ports/adapters.
2. Keep behavior unchanged.

Exit criteria:
- Existing behavior tests pass with new structure.

### Phase 4 - Contract and test taxonomy
1. Add contract tests for ports.
2. Finalize test folder split (`contracts`, `integration`, `hardware`).

Exit criteria:
- All test categories pass.
- Gate remains green.

## Agent ownership map for natural parallelism
1. Agent A - Domain and use-cases
- Owns: `src/dialogos/domain/*`, `src/dialogos/application/use_cases/*`, related unit tests.

2. Agent B - Ports and adapters
- Owns: `src/dialogos/ports/*`, `src/dialogos/adapters/*`, contract tests.

3. Agent C - UI shell
- Owns: `src/dialogos/ui/cli/*`, CLI wiring tests.

4. Agent D - Architecture enforcement
- Owns: `scripts/check_architecture.py`, `architecture_rules.toml`, `tests/architecture/*`, `Makefile` changes for arch checks.

5. Agent E - Docs/ADR/YAGNI onboarding
- Owns docs and spec updates listed in Workstream A and E.

6. Integrator
- Resolves cross-layer wiring, merge conflicts, and final gate run.

## Handoff contract (required from each agent)
Each agent returns exactly:
1. `changed_files`
2. `behavior_summary`
3. `pattern_and_layer_impact`
4. `tests_run`
5. `boundary_checks`
6. `assumptions`
7. `risks`
8. `out_of_scope`

## Acceptance criteria

### Functional and behavior
1. Milestone 1 behavior remains unchanged from user perspective.
2. CLI command entrypoint remains `dialogos` and `python3 -m dialogos`.

### Architecture
3. `cli.py` is reduced to wiring/shim responsibilities only.
4. No forbidden imports exist per architecture rules.
5. Domain logic remains side-effect free.

### Knowledge and onboarding
6. Bootstrap pack is sufficient for new agents to start a scoped task.
7. Deep-dive docs are optional and used only when required by task complexity.

### Testing and quality
8. Contract tests exist for all new/updated ports.
9. Architecture tests and gate checks are blocking.
10. `make gate` passes locally with hardware checks.

## Risks and mitigations
1. Risk: hidden behavior regressions during extraction.
- Mitigation: characterization tests before refactor + phase-gated merges.

2. Risk: over-engineering with unnecessary abstractions.
- Mitigation: each new module needs a concrete current use-case; no speculative ports.

3. Risk: enforcement script false positives.
- Mitigation: architecture test fixtures and rule exceptions with explicit ADR note.

4. Risk: onboarding docs become stale.
- Mitigation: docs updates required when layer boundaries change.

## Definition of done
Milestone 2 is done when:
1. The layer structure exists and is used by runtime code.
2. Architecture checker is in `make gate` and blocks violations.
3. Bootstrap/on-demand knowledge gradient docs are live and referenced from handoff docs.
4. All tests pass, including hardware checks.
5. Existing user behavior remains stable.

## Recommended first implementation slice
Start with the smallest high-leverage slice:
1. Add bootstrap docs + dependency rules + layer READMEs.
2. Add architecture checker + `test-arch` in gate.
3. Extract target resolution and confirm logic from `cli.py` into use-cases.

This slice produces immediate collaboration gains before full code migration.
