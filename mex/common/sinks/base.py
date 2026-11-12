from abc import abstractmethod
from collections.abc import Generator, Iterable
from typing import TypeVar

from pydantic import BaseModel as PydanticBaseModel

from mex.common.connector import BaseConnector

LoadItemT = TypeVar("LoadItemT", bound=PydanticBaseModel)


class BaseSink(BaseConnector):
    """Base class to define the interface of sink instances."""

    def __init__(self) -> None:
        """Create a new sink."""

    def close(self) -> None:
        """Close the sink."""

    @abstractmethod
    def load(
        self, items: Iterable[LoadItemT]
    ) -> Generator[LoadItemT, None, None]:  # pragma: no cover
        """Load the given items to a destination and yield them."""
        ...
