from os import PathLike
from pathlib import Path

from mex.common.assets.base import BaseAssetsConnector


class FilesystemAssetsConnector(BaseAssetsConnector):
    """Filesystem-based implementation of assets connector."""

    def __init__(self) -> None:  # pragma: no cover
        """Create a new connector instance."""

    def load_file(self, path: PathLike[str]) -> bytes:
        """Load a file from the filesystem.

        Args:
            path: The Path pointing to the file to load

        Returns:
            The file contents as bytes

        Raises:
            FileNotFoundError: If the file does not exist
            IOError: For other file access issues
        """
        # Read and return the file contents as bytes
        with Path(path).open("rb") as file_handle:
            return file_handle.read()

    def close(self) -> None:  # pragma: no cover
        """Close the connector's underlying sockets."""
