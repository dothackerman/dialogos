# Dialogos Milestone 3 - Agent-First Hardening (Debt Removal + Business-Rule Gate)

## Summary
Milestone 3 prepares Dialogos for first release-candidate development by removing remaining compatibility debt, simplifying runtime paths, and adding a business-rule regression gate.

This milestone is refactor-first and behavior-preserving:
1. Remove legacy/duplicate modules that keep multiple code paths alive.
2. Keep one canonical path per responsibility in the layered architecture.
3. Encode existing business rules as explicit catalog entries.
4. Gate rule regressions with automated checks and tests.

No new user-facing features are introduced in this milestone.

## Why this milestone exists
Milestone 2 established layered structure and architecture enforcement, but transitional compatibility modules remain. Those extra paths reduce agent confidence and make ownership less obvious during parallel work.

For agent-first multi-agent execution, we need:
1. Fewer equivalent places to implement behavior.
2. Stronger architecture checks that catch bypass imports.
3. Explicit business-rule regression coverage tied to current behavior.

## Relationship to prior specs
- Builds on: `specs/milestone-2-architecture.md`
- Preserves behavior from: `specs/mvp-push-to-talk.md`
- Legacy behavior contracts from Milestone 1 and 2 remain valid; this milestone changes structure and verification only.

## Objectives
1. Remove compatibility shims and duplicate legacy modules from runtime code.
2. Make architecture boundaries more explicit and harder to bypass.
3. Introduce a machine-readable business-rule catalog for current behavior.
4. Add business-rule regression checks to local quality flow.
5. Keep current runtime behavior unchanged from user perspective.

## Non-goals
1. No new product features.
2. No behavior redesign for tmux/audio/STT workflows.
3. No cloud CI introduction.
4. No speculative abstractions beyond current use-cases.

## Scope

### In scope
1. Subtractive refactor to remove legacy compatibility debt.
2. Entry-point cleanup to canonical CLI runtime module.
3. Architecture checker hardening for non-layer bypass imports.
4. Business-rule catalog definition for existing behavior.
5. Business-rule regression test and gate wiring.
6. Documentation updates required to keep onboarding and workflow intuitive.

### Out of scope
1. Always-on mode, TTS, or other deferred product ideas.
2. New adapter types (unless required for pure replacement of legacy path).
3. API or UX changes beyond compatibility-path removal.

## Legacy debt targeted for removal
Planned removals or full deprecation from runtime/test usage:
1. `src/dialogos/cli.py` (compat shim)
2. `src/dialogos/config.py`
3. `src/dialogos/logging_jsonl.py`
4. `src/dialogos/tmux_picker.py`
5. `src/dialogos/orchestrator.py`
6. `src/dialogos/contracts.py`
7. `src/dialogos/adapters/tmux_sender.py`

All behavior currently provided through these files must be preserved through canonical layered modules.

## Target post-milestone runtime shape
1. CLI entrypoint resolves directly to `dialogos.ui.cli.main:main`.
2. `python3 -m dialogos` resolves directly to `dialogos.ui.cli.main`.
3. Config and log storage behavior lives only in storage adapter path(s).
4. tmux target resolution behavior lives only in tmux adapter path(s).
5. Domain/application use-cases are the only business-rule execution path.

## Workstreams

### Workstream A - Subtractive architecture cleanup
1. Remove runtime imports and tests referencing legacy modules listed above.
2. Move any remaining required logic into canonical layer modules:
   - `ui/cli/*`
   - `application/use_cases/*`
   - `domain/*`
   - `ports/*`
   - `adapters/*`
3. Delete legacy files once no runtime/test references remain.
4. Update command entrypoints (`pyproject`, `__main__`, helper scripts) to canonical modules.

### Workstream B - Architecture guard hardening
1. Keep existing layer matrix enforcement.
2. Extend checker rules to fail on bypass patterns and any forbidden top-level runtime imports.
3. Add explicit architecture fixtures/tests for bypass cases.
4. Keep violation messages actionable (where code should move instead).

### Workstream C - Business-rule catalog and regression gate
1. Add a machine-readable business-rule catalog (developer-owned, non-spec file).
2. Catalog records for each existing rule:
   - stable rule ID
   - rule statement
   - owning layer
   - linked regression test(s)
3. Add a checker that validates:
   - each rule has at least one existing regression test mapping
   - mapped tests exist
4. Add regression command targets:
   - fast rule regression suite (non-hardware)
   - full rule regression suite (includes hardware where applicable)
5. Wire fast rule regression into local gate; full rule suite remains required for RC validation.

### Workstream D - Docs and onboarding clarity
1. Update onboarding docs so developers/agents can quickly decide where code belongs.
2. Add short decision guidance: "Where should this change live?"
3. Keep bootstrap docs concise and aligned with checker behavior and rule catalog workflow.
4. Update workflow/handoff docs to require rule IDs in change summaries when behavior is touched.

## Rule catalog initial baseline (must be captured)
At minimum, catalog and regress:
1. Target resolution precedence (`--tmux-target` -> env -> remembered -> picker).
2. No tmux session guidance + non-zero exit behavior.
3. Normal mode direct-send semantics.
4. Preview mode explicit-send confirm semantics (`send/edit/retry/skip/quit`).
5. Retry/skip/quit action behavior.
6. Empty transcript handling.
7. Send failure handling.
8. Config persistence behavior.
9. JSONL event schema and append behavior.
10. CUDA fallback behavior for STT runtime errors.
11. `--doctor` diagnostics behavior.

## Execution phases

### Phase 0 - Baseline lock
1. Confirm baseline gate is green on host.
2. Freeze rule baseline by identifying and listing current behavior rules.
3. Add or stabilize characterization tests for all baseline rules.

Exit criteria:
- Baseline behavior test set exists and passes.

### Phase 1 - Subtractive refactor
1. Migrate remaining logic from legacy modules into canonical modules.
2. Remove imports and references to legacy modules.
3. Delete legacy modules.
4. Keep behavior tests green.

Exit criteria:
- No runtime or tests import legacy modules.
- Entry points use canonical module path(s).

### Phase 2 - Checker hardening
1. Strengthen architecture checks for bypass imports.
2. Add checker tests/fixtures covering the new constraints.

Exit criteria:
- Intentional bypass imports fail `make test-arch`.

### Phase 3 - Business-rule gate integration
1. Add catalog validation script.
2. Add rule regression make targets.
3. Wire fast rule suite into `make gate`.
4. Keep full suite command for RC readiness validation.

Exit criteria:
- Gate fails when a cataloged rule loses test mapping or fails regression tests.

## Agent ownership map (parallel-friendly)
1. Agent A - Runtime simplification
   - Owns entrypoint cleanup and legacy-file removal in runtime modules.
2. Agent B - Adapters and ports cleanup
   - Owns adapter-side logic migration from legacy modules.
3. Agent C - Architecture enforcement
   - Owns checker/rules hardening and architecture tests.
4. Agent D - Rule catalog and regression harness
   - Owns catalog format, mapping checker, regression command wiring.
5. Agent E - Docs/onboarding
   - Owns workflow and quickstart updates aligned with new guardrails.
6. Integrator
   - Owns sequencing, merge conflict resolution, and final gate evidence.

## Handoff contract (required from each agent)
Each agent must return:
1. `changed_files`
2. `behavior_summary`
3. `rule_ids_touched` (if behavior-affecting code changed)
4. `tests_run`
5. `architecture_checks`
6. `assumptions`
7. `risks`
8. `out_of_scope`

## Acceptance criteria
1. Legacy modules listed in this spec are removed from runtime usage (and deleted when fully unused).
2. CLI and module entrypoints resolve through canonical UI runtime module.
3. `make test-arch` catches layer violations and bypass import patterns.
4. Business-rule catalog exists and is validated automatically.
5. Fast business-rule regression suite is part of `make gate`.
6. Full local gate remains green, including full tests on host hardware for RC validation.
7. User-visible behavior remains aligned with `specs/mvp-push-to-talk.md`.
8. Onboarding docs clearly explain where to place new code and how to validate rule regressions.

## Risks and mitigations
1. Risk: hidden regressions during legacy-file removal.
   - Mitigation: phase-0 characterization and rule-based regressions before deletion.
2. Risk: checker hardening creates developer friction.
   - Mitigation: keep error messages directive and docs synchronized.
3. Risk: rule catalog becomes stale.
   - Mitigation: require catalog/test mapping updates whenever behavior rules change.
4. Risk: overbuilding tooling.
   - Mitigation: keep catalog schema minimal and focused on existing business rules only.

## Definition of done
Milestone 3 is done when:
1. Compatibility debt listed in scope is removed.
2. Architecture enforcement blocks known bypass patterns.
3. Business-rule catalog and regression gate are active.
4. Runtime behavior remains unchanged and validated through regression tests.
5. Documentation makes the agent/developer path intuitive and safe for parallel feature work.
