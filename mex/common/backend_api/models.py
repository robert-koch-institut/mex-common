from typing import Annotated

from pydantic import Field, TypeAdapter

from mex.common.identity.models import Identity
from mex.common.models import (
    AnyExtractedModel,
    AnyMergedModel,
    AnyPreviewModel,
    AnyRuleSetResponse,
    BaseModel,
)
from mex.common.types import Identifier


class ExtractedItemsRequest(BaseModel):
    """Request model for a list of extracted items."""

    items: list[AnyExtractedModel]


class ExtractedItemsResponse(BaseModel):
    """Response model for a list of extracted items including a total count."""

    items: list[AnyExtractedModel]
    total: int


class MergedItemsResponse(BaseModel):
    """Response model for a list of merged items including a total count."""

    items: list[AnyMergedModel]
    total: int


class PreviewItemsResponse(BaseModel):
    """Response model for a list of preview items including a total count."""

    items: list[AnyPreviewModel]
    total: int


class IdentitiesResponse(BaseModel):
    """Response models for a list of identities."""

    items: list[Identity]


class IdentifiersResponse(BaseModel):
    """Response models for a list of identifiers."""

    identifiers: list[Identifier]


MergedModelTypeAdapter: TypeAdapter[AnyMergedModel] = TypeAdapter(
    Annotated[AnyMergedModel, Field(discriminator="entityType")]
)
RuleSetResponseTypeAdapter: TypeAdapter[AnyRuleSetResponse] = TypeAdapter(
    Annotated[AnyRuleSetResponse, Field(discriminator="entityType")]
)
