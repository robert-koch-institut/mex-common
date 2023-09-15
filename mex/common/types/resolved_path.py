from abc import ABCMeta, abstractmethod
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any, Type, TypeVar, Union

from pydantic_core import core_schema

if TYPE_CHECKING:  # pragma: no cover
    from mex.common.settings import BaseSettings

ResolvedPathT = TypeVar("ResolvedPathT", bound="ResolvedPath")


class ResolvedPath(PathLike[str], metaclass=ABCMeta):
    """Custom path for settings that can be absolute or relative to another setting."""

    __slots__ = ("_path",)

    _path: Path

    def __init__(self, path: Union[str, Path, "ResolvedPath"]) -> None:
        """Create a new resolved path instance."""
        if isinstance(path, str):
            path = Path(path)
        elif isinstance(path, ResolvedPath):
            path = path._path
        self._path = path

    def __fspath__(self) -> str:
        """Return the file system path representation."""
        return self.resolve().__fspath__()

    @classmethod
    @abstractmethod
    def __get_base_path__(cls, settings: "BaseSettings") -> Path:  # pragma: no cover
        """Return the base path that relative paths will follow."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Type[Any]) -> core_schema.CoreSchema:
        """Set schema to str schema."""
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls: type[ResolvedPathT], value: Any) -> "ResolvedPathT":
        """Convert a string value to a Text instance."""
        if isinstance(value, (str, Path, ResolvedPath)):
            return cls(value)
        raise ValueError(f"Cannot parse {type(value)} as {cls.__name__}")

    def resolve(self) -> Path:
        """Lazily resolve the underlying path to an absolute path.

        If the underlying path already is absolute, it is returned as-is.
        If it is relative, the concrete subclass of `ResolvedPath` gets to
        decide what it is relative to. We read the settings from the current
        `SettingsContext` and pick a base path from there.
        """
        from mex.common.settings import SettingsContext  # noqa

        if self._path.is_absolute():
            return self._path
        if settings := SettingsContext.get():
            return self.__get_base_path__(settings) / self._path
        raise RuntimeError("Cannot find base path because settings are not loaded")

    def raw(self) -> Path:
        """Return the raw underlying path without resolving it."""
        return self._path

    def __str__(self) -> str:
        """Return a string rendering of the resolved path."""
        return self.resolve().as_posix()

    def __repr__(self) -> str:
        """Return a representation string of the resolved path."""
        return f'{self.__class__.__name__}("{self}")'


class AssetsPath(ResolvedPath):
    """Custom path for settings that can be absolute or relative to `assets_dir`."""

    @classmethod
    def __get_base_path__(cls, settings: "BaseSettings") -> Path:
        """Return the `assets_dir` as a base path that relative paths will follow."""
        return settings.assets_dir


class WorkPath(ResolvedPath):
    """Custom path for settings that can be absolute or relative to `work_dir`."""

    @classmethod
    def __get_base_path__(cls, settings: "BaseSettings") -> Path:
        """Return the `work_dir` as a base path that relative paths will follow."""
        return settings.work_dir
