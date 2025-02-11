from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ItemsContainer(BaseModel, Generic[T]):
    """Generic container that contains items."""

    items: list[T]


class PaginatedItemsContainer(BaseModel, Generic[T]):
    """Generic container that contains items and has a total item count."""

    items: list[T]
    total: int
