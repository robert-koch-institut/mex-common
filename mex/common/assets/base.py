from abc import abstractmethod

from mex.common.connector import BaseConnector
from mex.common.types import AssetsPath

class BaseAssetsConnector(BaseConnector):
    """Base class for assets connectors that handle file loading."""

    @abstractmethod
    def load_file(self, path: AssetsPath) -> bytes:
        """Load a file from the given AssetsPath and return bytes.

        Args:
            path: The AssetsPath pointing to the file to load

        Returns:
            The file contents as bytes

        Raises:
            FileNotFoundError: If the file does not exist
            IOError: For other file access issues
        """