from typing import Annotated, Generic, TypeVar

from pydantic import Field, TypeAdapter

from mex.common.models import AnyMergedModel, AnyRuleSetResponse, BaseModel
from mex.common.types import Identifier

T = TypeVar("T")


class ItemsContainer(BaseModel, Generic[T]):
    """Generic container that contains items."""

    items: list[T]


class PaginatedItemsContainer(BaseModel, Generic[T]):
    """Generic container that contains items and has a total item count."""

    items: list[T]
    total: int


class IdentifiersResponse(BaseModel):
    """Response models for a list of identifiers."""

    identifiers: list[Identifier]


MergedModelTypeAdapter: TypeAdapter[AnyMergedModel] = TypeAdapter(
    Annotated[AnyMergedModel, Field(discriminator="entityType")]
)
RuleSetResponseTypeAdapter: TypeAdapter[AnyRuleSetResponse] = TypeAdapter(
    Annotated[AnyRuleSetResponse, Field(discriminator="entityType")]
)
