# Dialogos

Dialogos creates a local voice channel from Linux microphone input to a selected Codex tmux pane:
1. Push-to-talk capture
2. Local transcription with `faster-whisper`
3. Full confirm control before send
4. Send confirmed text to tmux
5. Persist target/config and JSONL turn logs

Milestone status: **Milestone 2 architecture migration target** (runtime behavior from Milestone 1 remains unchanged).

## Why the name "Dialogos"?

"Dialogos" comes from the Greek root associated with dialogue and exchange.
The project goal matches that meaning: a natural conversational channel between human speech and Codex.

## Architecture snapshot

Target dependency direction is strict:
- `ui -> application -> domain`
- `application -> ports`
- `adapters -> ports`
- `ui` composes adapters and wires use-cases

Reference docs:
- [Architecture](docs/dev/architecture.md)
- [Patterns Quickstart](docs/dev/patterns-quickstart.md)
- [Dependency Rules](docs/dev/dependency-rules.md)
- [ADR Index](docs/dev/adr/README.md)

## Development commands

```bash
make install
make install-dev
make hooks
make test-arch
make check
make test-fast
make test
make gate
```

## Documentation map

### User-facing
- [Quickstart](docs/user/quickstart.md)
- [Capabilities](docs/user/capabilities.md)
- [Dependencies](docs/user/dependencies.md)

### Agent-facing
- [Agent Roles](docs/agents/roles.md)
- [Agent Workflow](docs/agents/workflow.md)
- [New Session Handoff](docs/agents/new-session-handoff.md)

### Developer-only
- [Architecture](docs/dev/architecture.md)
- [Patterns Quickstart](docs/dev/patterns-quickstart.md)
- [Dependency Rules](docs/dev/dependency-rules.md)
- [Patterns Deep Dive](docs/dev/patterns-deep-dive.md)
- [ADR Index](docs/dev/adr/README.md)
- [Deferred Ideas](docs/dev/deferred-ideas.md)

## License

MIT. See [LICENSE](LICENSE).
