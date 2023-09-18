from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator

from mex.common.models import BaseModel
from mex.common.types import (
    Identifier,
    Link,
    LinkLanguage,
    Text,
    TextLanguage,
    Timestamp,
)

PublicApiFieldValueTypes = UUID | Enum | Timestamp | str | Link | Text
PublicApiFieldValueTypesOrList = (
    PublicApiFieldValueTypes | list[PublicApiFieldValueTypes]
)


class PublicApiBaseModel(BaseModel):
    """Common Public API base class."""

    model_config = ConfigDict(extra="ignore", str_min_length=0)


class PublicApiAxisConstraint(PublicApiBaseModel):
    """Axis constraints for Public API search requests."""

    axis: str
    combineOperator: str = "and"
    type: str = "exact"
    values: list[str]


class PublicApiSearchRequest(PublicApiBaseModel):
    """Request body for Public API search requests."""

    axisConstraints: list[PublicApiAxisConstraint] = []
    fields: list[str] = []
    limit: int = 10
    offset: int = 0
    query: str = "*"


class PublicApiField(PublicApiBaseModel):
    """A single field of an item as represented in the Public API format."""

    fieldName: str = Field(..., include=True)
    fieldValue: PublicApiFieldValueTypesOrList = Field(..., include=True)
    language: LinkLanguage | TextLanguage | None = Field(None, include=True)

    @field_validator("language", mode="before")
    @classmethod
    def fix_language(cls, value: Any) -> Any:
        """Only try to parse languages when the string is non-empty."""
        if isinstance(value, str) and value.strip() == "":
            return None
        return value


class PublicApiItem(PublicApiBaseModel):
    """Public API item representing an entity or extracted data model."""

    entityType: str = Field(..., include=True)
    itemId: UUID | None = None
    businessId: str
    values: list[PublicApiField] = Field(..., include=True)

    @property
    def stableTargetId(self) -> Identifier:
        """Return the stableTargetId of this item."""
        return Identifier(self.businessId.removesuffix("#"))


class PublicApiSearchResponse(PublicApiBaseModel):
    """Response body that is expected for search results."""

    items: list[PublicApiItem]
    numFound: int


class PublicApiAuthResponse(PublicApiBaseModel):
    """Response body that is expected for auth requests."""

    access_token: str
    refresh_token: str | None = None
    token_type: str
    expires_in: int


class PublicApiItemWithoutValues(PublicApiBaseModel):
    """Public API item representing an entity or extracted data model."""

    entityType: str = Field(..., include=True)
    itemId: UUID | None = None
    businessId: str

    @property
    def stableTargetId(self) -> Identifier:
        """Return the stableTargetId of this item."""
        return Identifier(self.businessId.removesuffix("#"))


class PublicApiMetadataItemsResponse(PublicApiBaseModel):
    """Response body that is expected for the metadata items endpoint."""

    items: list[PublicApiItemWithoutValues]
    next: UUID | Literal[""]


class PublicApiJobItemsResponse(PublicApiBaseModel):
    """Response body that is expected for the jobs items endpoint."""

    jobId: UUID
    itemIds: list[UUID | Literal["{}"]]
