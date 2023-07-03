import platform
from pathlib import Path

from pydantic import BaseModel

from mex.common.types import AssetsPath


def test_resolve() -> None:
    if platform.system() == "Windows":  # pragma: no cover
        absolute = Path(r"C:\absolute\path")
    else:
        absolute = Path("/absolute/path")
    assert absolute.is_absolute()
    assert AssetsPath(absolute).resolve().is_absolute()

    relative = Path("relative", "path")
    assert not relative.is_absolute()
    assert AssetsPath(relative).resolve().is_absolute()


def test_raw() -> None:
    relative = Path("relative", "path")
    assert AssetsPath(relative).raw() == relative


def test_validate() -> None:
    class TestModel(BaseModel):
        path_attr: AssetsPath

    model = TestModel(path_attr=r"C:\Win32\AppRoaming\registry.dll")
    assert isinstance(model.path_attr, AssetsPath)

    model = TestModel(path_attr=Path("/dev0/mount/etc/bin/make.sh"))
    assert isinstance(model.path_attr, AssetsPath)

    model = TestModel(path_attr=AssetsPath(Path("/usr/share/local/etc/swap")))
    assert isinstance(model.path_attr, AssetsPath)


def test_str() -> None:
    if platform.system() == "Windows":  # pragma: no cover
        path = AssetsPath.validate(r"C:\absolute\path")
        assert str(path) == "C:/absolute/path"
    else:
        path = AssetsPath.validate("/absolute/path")
        assert str(path) == "/absolute/path"


def test_repr() -> None:
    if platform.system() == "Windows":  # pragma: no cover
        path = AssetsPath.validate(r"C:\absolute\path")
        assert repr(path) == 'AssetsPath("C:/absolute/path")'
    else:
        path = AssetsPath.validate("/absolute/path")
        assert repr(path) == 'AssetsPath("/absolute/path")'
