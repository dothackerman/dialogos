# New Session Handoff

## Read first (bootstrap pack)
1. `AGENTS.md`
2. `docs/dev/patterns-quickstart.md`
3. `docs/dev/dependency-rules.md`
4. `docs/agents/workflow.md`

## Read on-demand (task-dependent)
1. `docs/dev/patterns-deep-dive.md`
2. `docs/dev/adr/README.md` and related ADR file(s)
3. `src/dialogos/<layer>/README.md` for touched layer(s)
4. `specs/milestone-2-architecture.md` for migration context

## Execution rule
- Implement exactly approved scope from the active spec.
- Preserve MVP runtime behavior unless the spec explicitly changes behavior.
- Run `make test-arch` and `make gate` before final push.

Kickoff prompt for a new Codex session:

```text
Read AGENTS.md, docs/dev/patterns-quickstart.md, and docs/dev/dependency-rules.md first. Then execute the assigned scope and keep layer boundaries strict.
```
