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
        msg = "given path is not valid or not in assets directory"
        try:
            target_path = (self._assets_dir / path).resolve(strict=True)
        except OSError:
            raise PermissionError(msg) from None
        if not target_path.is_relative_to(self._assets_dir):
            raise PermissionError(msg)
        with target_path.open("rb") as file_handle:
            return file_handle.read()

    def close(self) -> None:
        """Nothing to close for filesystem access."""
