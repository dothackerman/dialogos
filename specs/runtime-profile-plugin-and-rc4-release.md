# Silicato Runtime Profile Plugin Architecture + RC4 Release Sync

Status: Implemented
Created on: 2026-03-08

## Problem

The current `spawn` behavior is implemented as a hardcoded CLI profile path, not a plugin boundary.
This makes runtime customization harder and couples core CLI runtime logic to one preset strategy.

Documentation and release metadata also need to be synchronized for the next release candidate.

## Goal

1. Refactor runtime profile selection into a plugin-style architecture.
2. Implement `spawn` as a runtime plugin.
3. Keep core runtime behavior functional without spawn-specific branching.
4. Synchronize docs and release metadata for `0.1.0rc4`.

## Scope

1. Add a runtime plugin interface and plugin registry in the CLI layer.
2. Move spawn profile logic into a dedicated spawn plugin implementation.
3. Update CLI wiring to resolve runtime settings through plugin abstraction.
4. Keep CLI UX (`--profile`, `--spawn`) coherent and tested.
5. Update user/dev docs and changelog for `0.1.0rc4`.
6. Keep release commands/documentation aligned with current release flow.

## Non-goals

1. No change to core turn flow semantics (`send/edit/retry/skip/quit`).
2. No tmux transport redesign.
3. No architecture layer boundary relaxation.

## Acceptance Criteria

1. Core CLI runtime no longer contains spawn-specific tuning logic.
2. Spawn behavior is encapsulated in a plugin implementation.
3. Plugin selection is tested end-to-end in CLI runtime wiring.
4. Docs and CLI helper text describe runtime plugin behavior coherently.
5. Version and changelog are synchronized to `0.1.0rc4`.
6. `make gate`, `make test-rules`, and `make test-e2e-tmux` pass.
