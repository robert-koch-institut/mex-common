from typing import Generic, TypeVar

from pydantic import BaseModel as PydanticBaseModel

_ContainerItemT = TypeVar("_ContainerItemT")


class ItemsContainer(PydanticBaseModel, Generic[_ContainerItemT]):
    """Generic container that contains items."""

    items: list[_ContainerItemT]


class PaginatedItemsContainer(PydanticBaseModel, Generic[_ContainerItemT]):
    """Generic container that contains items and has a total item count."""

    items: list[_ContainerItemT]
    total: int
