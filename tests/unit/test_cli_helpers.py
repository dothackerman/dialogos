from dialogos.cli import is_cuda_runtime_missing


def test_is_cuda_runtime_missing_true() -> None:
    err = RuntimeError("Library libcublas.so.12 is not found or cannot be loaded")
    assert is_cuda_runtime_missing(err)


def test_is_cuda_runtime_missing_false() -> None:
    err = RuntimeError("some unrelated runtime error")
    assert not is_cuda_runtime_missing(err)
