from pathlib import Path

from mex.common.settings import BaseSettings
from mex.common.types import AssetsPath

from .base import BaseAssetsConnector

class FilesystemAssetsConnector(BaseAssetsConnector):
    """Filesystem-based implementation of assets connector."""

    def load_file(self, path: AssetsPath) -> bytes:
        """Load a file from the filesystem.

        Args:
            path: The AssetsPath pointing to the file to load

        Returns:
            The file contents as bytes

        Raises:
            FileNotFoundError: If the file does not exist
            IOError: For other file access issues
        """
        # Resolve the AssetsPath to an absolute path
        settings = BaseSettings.get()
        resolved_path = settings.resolve_assets_path(path)

        # Read and return the file contents as bytes
        with Path(resolved_path).open("rb") as file_handle:
            return file_handle.read()

    def close(self) -> None:
        """Close the connector (no-op for filesystem)."""
        pass