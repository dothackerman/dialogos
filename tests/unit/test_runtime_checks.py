from __future__ import annotations

import pytest

from dialogos.ui.cli.runtime_checks import require_binary, run_doctor


def test_require_binary_exits_with_guidance_when_missing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("dialogos.ui.cli.runtime_checks.shutil.which", lambda _: None)

    with pytest.raises(SystemExit, match="1"):
        require_binary("tmux", apt_package="tmux")

    captured = capsys.readouterr()
    assert "Missing required binary: tmux" in captured.err
    assert "sudo apt install tmux" in captured.err


def test_run_doctor_reports_missing_binaries(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("dialogos.ui.cli.runtime_checks.shutil.which", lambda _: None)

    code = run_doctor()
    captured = capsys.readouterr()

    assert code == 0
    assert "- arecord: MISSING" in captured.out
    assert "- tmux: MISSING" in captured.out
    assert "- ffmpeg: MISSING" in captured.out
