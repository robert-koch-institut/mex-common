from os import PathLike
from pathlib import Path
from typing import Any, Union

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class PathWrapper(PathLike[str]):
    """Custom path for settings that can be absolute or relative to another setting."""

    _path: Path

    def __init__(self, path: Union[str, Path, "PathWrapper"]) -> None:
        """Create a new resolved path instance."""
        if isinstance(path, str):
            path = Path(path)
        elif isinstance(path, PathWrapper):
            path = path._path  # noqa: SLF001
        self._path = path

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """Modify the core schema to add validation and serialization rules."""
        return core_schema.chain_schema(
            [
                core_schema.is_instance_schema(str | Path | PathWrapper),
                core_schema.no_info_plain_validator_function(cls),
            ],
            serialization=core_schema.to_string_ser_schema(when_used="unless-none"),
        )

    def __fspath__(self) -> str:
        """Return the file system path representation."""
        return self._path.__fspath__()

    def __truediv__(self, other: str | PathLike[str]) -> Path:
        """Return a joined path on the basis of `/`."""
        return self._path.__truediv__(other)

    def __hash__(self) -> int:
        """Return the hash for this object."""
        return hash(self._path)

    def __str__(self) -> str:
        """Return a string rendering of the resolved path."""
        return self._path.as_posix()

    def __repr__(self) -> str:
        """Return a representation string of the resolved path."""
        return f'{self.__class__.__name__}("{self}")'

    def __eq__(self, other: object) -> bool:
        """Return true for two PathWrappers with equal paths."""
        if isinstance(other, PathWrapper):
            return self._path.__eq__(other._path)
        msg = f"Can't compare {type(other)} with {type(self)}"
        raise TypeError(msg)

    def is_absolute(self) -> bool:
        """True if the underlying path is absolute."""
        return self._path.is_absolute()

    def is_relative(self) -> bool:
        """True if the underlying path is relative."""
        return not self._path.is_absolute()


class AssetsPath(PathWrapper):
    """Custom path for settings that can be absolute or relative to `assets_dir`."""


class WorkPath(PathWrapper):
    """Custom path for settings that can be absolute or relative to `work_dir`."""
