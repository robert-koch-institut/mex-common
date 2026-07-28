from abc import abstractmethod

from mex.common.connector import BaseConnector


class BaseAssetsConnector(BaseConnector):
    """Base class for assets connectors that handle file loading."""

    @abstractmethod
    def read(self, path: str) -> bytes:
        """Read a file from the given path and return bytes.

        Args:
            path: The path pointing to the file to read

        Returns:
            The file contents as bytes

        Raises:
            PermissionError: For file access permission issues
        """
        ...

    @abstractmethod
    def glob(self, path: str, pattern: str) -> list[str]:
        """Return the list of file names from a given path.

        Args:
            path: The path pointing to the file to read
            pattern: pattern to match

        Returns:
            List of file names
        """
        ...
