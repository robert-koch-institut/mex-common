from pathlib import Path

import pytest

from mex.common.types import PathWrapper


def test_path_wrapper_instantiation() -> None:
    assert PathWrapper(Path("foo", "bar"))._path == Path("foo", "bar")
    assert PathWrapper("foo/bar")._path == Path("foo", "bar")
    assert PathWrapper(PathWrapper("foo/bar"))._path == Path("foo", "bar")


def test_path_wrapper_fspath() -> None:
    assert (
        PathWrapper(Path("foo") / "bar").__fspath__() == Path("foo", "bar").__fspath__()
    )


def test_path_wrapper_slash() -> None:
    assert PathWrapper(Path("foo")) / "bar" == PathWrapper(Path("foo") / "bar")._path


def test_path_wrapper_string() -> None:
    assert str(PathWrapper(Path("foo", "bar"))) == Path("foo", "bar").as_posix()


def test_path_wrapper_representation() -> None:
    assert repr(PathWrapper(Path("foo", "bar"))).startswith("PathWrapper")


def test_path_wrapper_equality() -> None:
    assert PathWrapper(Path("foo", "bar")) == PathWrapper(Path("foo", "bar"))
    assert PathWrapper(Path("foo", "bar")) != PathWrapper(Path("bar", "batz"))

    with pytest.raises(TypeError):
        _ = PathWrapper("foo") == 42


def test_path_wrapper_relative_absolute() -> None:
    assert PathWrapper("/foo/bar").is_absolute() == Path("/foo/bar").is_absolute()
    assert (
        PathWrapper("C:\\foo\\bar").is_absolute() == Path("C:\\foo\\bar").is_absolute()
    )
    assert PathWrapper("bar/batz").is_relative() != Path("bar/batz").is_absolute()
