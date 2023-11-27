import sys
from pathlib import Path, PosixPath, WindowsPath
from typing import Any
from warnings import warn

if sys.platform == "win32":
    path_type = WindowsPath
else:
    path_type = PosixPath


class _DeprecatedResolvedPath(path_type):
    """Class to support the deprecated .resolve() and .raw() methods."""

    def resolve(self, *args: Any, **kwargs: Any) -> Path:  # type: ignore
        """Return absolute path."""
        warn("deprecated", DeprecationWarning)
        return super().resolve(*args, **kwargs)


class AssetsPath(
    _DeprecatedResolvedPath
):  # TODO: inherit from path_type instead after removal of deprecated class
    """Custom path for settings that can be absolute or relative to `assets_dir`."""


class WorkPath(
    _DeprecatedResolvedPath
):  # TODO: inherit from path_type instead after removal of deprecated class
    """Custom path for settings that can be absolute or relative to `work_dir`."""
