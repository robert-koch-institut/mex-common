from abc import ABCMeta, abstractmethod
from contextlib import ExitStack, closing
from typing import Self, cast, final

from mex.common.context import SingletonStore
from mex.common.transform import dromedary_to_snake


class _ConnectorStore(SingletonStore["BaseConnector"]):
    """Thin wrapper for storing thread-local singletons of connectors."""

    def reset(self) -> None:
        """Close all connectors and remove them from the singleton store."""
        with ExitStack() as stack:
            for connector in self:
                stack.push(closing(connector))
        super().reset()

    def metrics(self) -> dict[str, int]:
        """Generate metrics about all active connectors."""
        return {
            f"{dromedary_to_snake(connector.__class__.__name__)}_{metric_key}": value
            for connector in self
            for metric_key, value in connector.metrics().items()
        }


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

    def metrics(self) -> dict[str, int]:  # pragma: no cover
        """Generate metrics about connector usage."""
        return {}

    @abstractmethod
    def close(self) -> None:  # pragma: no cover
        """Close the connector's underlying sockets."""
