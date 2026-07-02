from abc import abstractmethod
from os import PathLike

from mex.common.connector import BaseConnector


class BaseAssetsConnector(BaseConnector):
    """Base class for assets connectors that handle file loading."""

    @abstractmethod
    def load_file(self, path: PathLike[str]) -> bytes:
        """Load a file from the given Path and return bytes.

        Args:
            path: The Path pointing to the file to load

        Returns:
            The file contents as bytes

        Raises:
            FileNotFoundError: If the file does not exist
            IOError: For other file access issues
        """
        ...
