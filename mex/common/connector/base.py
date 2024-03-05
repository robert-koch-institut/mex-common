from abc import ABCMeta, abstractmethod
from contextlib import ExitStack
from types import TracebackType
from typing import Optional, TypeVar, cast, final

from mex.common.context import ContextStore

ConnectorType = TypeVar("ConnectorType", bound="BaseConnector")
ConnectorContext = ContextStore[dict[type["BaseConnector"], "BaseConnector"]]({})


def reset_connector_context() -> None:
    """Close all connectors and remove them from current context."""
    with ExitStack() as stack:
        for connector in ConnectorContext.get().values():
            stack.push(connector)


class BaseConnector(metaclass=ABCMeta):
    """Base class for connectors that are handled as a context manager."""

    @final
    @classmethod
    def get(cls: type[ConnectorType]) -> ConnectorType:
        """Create or retrieve a connector singleton from the context variable.

        Returns:
            Instance of the connector
        """
        context = ConnectorContext.get()
        try:
            connector = cast(ConnectorType, context[cls])
        except KeyError:
            context[cls] = connector = cls()
        return connector

    @abstractmethod
    def __init__(self) -> None:  # pragma: no cover
        """Create a new connector instance."""

    @final
    def __enter__(self: ConnectorType) -> ConnectorType:
        """Make connector available as context manager target."""
        return self

    @final
    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit connector by calling `close` method and removing it from context."""
        self.close()
        context = ConnectorContext.get()
        context.pop(type(self))

    @abstractmethod
    def close(self) -> None:  # pragma: no cover
        """Close the connector's underlying sockets."""
