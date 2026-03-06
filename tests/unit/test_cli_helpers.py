from __future__ import annotations

from silicato.adapters.stt.whisper import is_cuda_runtime_missing
from silicato.application.use_cases.resolve_target import ResolveTargetUseCase
from silicato.ports.targeting import InvalidTmuxTargetError, PaneEntry


class FakeTargetResolver:
    def __init__(self) -> None:
        self.validated: list[str] = []
        self.should_fail_target: str | None = None
        self.panes: list[PaneEntry] = []
        self.picked: str = ""

    def validate_target(self, target: str) -> None:
        self.validated.append(target)
        if self.should_fail_target and target == self.should_fail_target:
            raise InvalidTmuxTargetError("bad")

    def list_panes(self) -> list[PaneEntry]:
        return self.panes

    def pick_target_interactive(self, panes: list[PaneEntry], **kwargs: object) -> str:
        _ = panes
        _ = kwargs
        return self.picked

    def print_no_tmux_guidance(self, **kwargs: object) -> None:
        _ = kwargs


def test_is_cuda_runtime_missing_true() -> None:
    err = RuntimeError("Library libcublas.so.12 is not found or cannot be loaded")
    assert is_cuda_runtime_missing(err)


def test_is_cuda_runtime_missing_false() -> None:
    err = RuntimeError("some unrelated runtime error")
    assert not is_cuda_runtime_missing(err)


def test_resolve_tmux_target_prefers_cli() -> None:
    resolver = FakeTargetResolver()
    use_case = ResolveTargetUseCase(resolver)

    result = use_case.execute(
        explicit_target="cli:0.1",
        pick_target=False,
        env_target="env:0.1",
        remembered_target="cfg:0.1",
    )

    assert result.target == "cli:0.1"
    assert resolver.validated == ["cli:0.1"]


def test_resolve_tmux_target_falls_back_to_picker_for_invalid_config() -> None:
    resolver = FakeTargetResolver()
    resolver.should_fail_target = "bad:target"
    resolver.panes = [PaneEntry(target="picked:0.1", command="bash", title="main")]
    resolver.picked = "picked:0.1"
    use_case = ResolveTargetUseCase(resolver)

    result = use_case.execute(
        explicit_target=None,
        pick_target=False,
        env_target=None,
        remembered_target="bad:target",
    )

    assert result.target == "picked:0.1"
    assert result.remembered_target_error == "bad"


def test_resolve_tmux_target_uses_env_when_available() -> None:
    resolver = FakeTargetResolver()
    use_case = ResolveTargetUseCase(resolver)

    result = use_case.execute(
        explicit_target=None,
        pick_target=False,
        env_target="env:0.5",
        remembered_target=None,
    )

    assert result.target == "env:0.5"
    assert resolver.validated == ["env:0.5"]
