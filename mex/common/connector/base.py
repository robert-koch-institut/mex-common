from abc import ABCMeta, abstractmethod
from contextlib import ExitStack, closing
from typing import Self, cast, final

from mex.common.context import SingletonStore


class _ConnectorStore(SingletonStore["BaseConnector"]):
    """Thin wrapper for storing thread-local singletons of connectors."""

    def reset(self) -> None:
        """Close all connectors and remove them from the singleton store."""
        with ExitStack() as stack:
            for connector in self:
                stack.push(closing(connector))
        super().reset()


CONNECTOR_STORE = _ConnectorStore()


class BaseConnector(metaclass=ABCMeta):
    """Base class for connectors that are handled as singletons."""

    @final
    @classmethod
    def get(cls) -> Self:
        """Get the singleton instance for this class from the store."""
        return cast("Self", CONNECTOR_STORE.load(cls))

    @abstractmethod
    def __init__(self) -> None:  # pragma: no cover
        """Create a new connector instance."""

    @abstractmethod
    def close(self) -> None:  # pragma: no cover
        """Close the connector's underlying sockets."""
