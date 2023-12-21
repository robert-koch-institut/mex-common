from os import PathLike
from pathlib import Path
from typing import Any, Type, TypeVar, Union
from warnings import warn

from pydantic_core import core_schema

PathWrapperT = TypeVar("PathWrapperT", bound="PathWrapper")


class PathWrapper(PathLike[str]):
    """Custom path for settings that can be absolute or relative to another setting."""

    _path: Path

    def __init__(self, path: Union[str, Path, "PathWrapper"]) -> None:
        """Create a new resolved path instance."""
        if isinstance(path, PathWrapper):
            path = path._path
        elif isinstance(path, str):
            path = Path(path)
        self._path = path

    def __fspath__(self) -> str:
        """Return the file system path representation."""
        return self._path.__fspath__()

    def __truediv__(self, other: str | PathLike[str]) -> Path:
        """Return a joined path on the basis of `/`."""
        return self._path.__truediv__(other)

    def __str__(self) -> str:
        """Return a string rendering of the resolved path."""
        return self._path.as_posix()

    def __repr__(self) -> str:
        """Return a representation string of the resolved path."""
        return f'{self.__class__.__name__}("{self}")'

    def __eq__(self, other: Any) -> bool:
        """Return true for two PathWrappers with equal paths."""
        if isinstance(other, PathWrapper):
            return self._path.__eq__(other._path)
        raise TypeError(f"Can't compare {type(other)} with {type(self)}")

    def is_absolute(self) -> bool:
        """True if the underlying path is absolute."""
        return self._path.is_absolute()

    def is_relative(self) -> bool:
        """True if the underlying path is relative."""
        return not self._path.is_absolute()

    def resolve(self) -> Path:
        """Return the resolved path which is the underlying path."""
        warn("deprecated", DeprecationWarning)
        return self._path

    def raw(self) -> Path:
        """Return the raw underlying path without resolving it."""
        warn("deprecated", DeprecationWarning)
        return self._path

    @classmethod
    def __get_pydantic_core_schema__(cls, _source: Type[Any]) -> core_schema.CoreSchema:
        """Set schema to str schema."""
        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(
                    cls.validate,
                ),
            ]
        )
        from_anything_schema = core_schema.chain_schema(
            [
                core_schema.no_info_plain_validator_function(cls.validate),
                core_schema.is_instance_schema(PathWrapper),
            ]
        )
        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=from_anything_schema,
        )

    @classmethod
    def validate(cls: type[PathWrapperT], value: Any) -> PathWrapperT:
        """Convert a string value to a Text instance."""
        if isinstance(value, (str, Path, PathWrapper)):
            return cls(value)
        raise ValueError(f"Cannot parse {type(value)} as {cls.__name__}")


class AssetsPath(PathWrapper):
    """Custom path for settings that can be absolute or relative to `assets_dir`."""


class WorkPath(PathWrapper):
    """Custom path for settings that can be absolute or relative to `work_dir`."""
