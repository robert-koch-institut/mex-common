from pathlib import Path

from mex.common.assets.base import BaseAssetsConnector
from mex.common.settings import BaseSettings


class FilesystemAssetsConnector(BaseAssetsConnector):
    """Filesystem-based implementation of assets connector."""

    def __init__(self) -> None:
        """Create a new connector instance."""
        self._assets_dir = BaseSettings.get().assets_dir

    def read(self, path: str) -> bytes:
        """Read a file from the filesystem.

        Args:
            path: The path pointing to the file to load

        Returns:
            The file contents as bytes

        Raises:
            PermissionError: For file access permission issues
        """
        resolved_path = self._resolve_path_and_check_permission(path)
        with resolved_path.open("rb") as file_handle:
            return file_handle.read()

    def glob(self, path: str, pattern: str) -> list[str]:
        """Return the list of file names from a given path from the file system.

        Args:
            path: The path pointing to the file to read
            pattern: pattern to match

        Returns:
            List of file names

        Raises:
            PermissionError: For file access permission issues
        """
        resolved_path = self._resolve_path_and_check_permission(path)
        return [
            str(self._resolve_path_and_check_permission(str(file_path)))
            for file_path in resolved_path.glob(pattern=pattern)
        ]

    def close(self) -> None:
        """Nothing to close for filesystem access."""

    def _resolve_path_and_check_permission(self, path: str) -> Path:
        """Resolve a path and check whether path is permitted.

        Args:
            path: The path pointing to the file to load

        Returns:
            resolved path

        Raises:
            PermissionError: For file access permission issues
        """
        msg = "given path is not valid or not in assets directory"
        try:
            resolved_path = (self._assets_dir / path).resolve(strict=True)
        except OSError:
            raise PermissionError(msg) from None
        if not resolved_path.is_relative_to(self._assets_dir):
            raise PermissionError(msg)
        return resolved_path
