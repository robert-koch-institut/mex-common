from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import (
    ExtractedPrimarySourceIdentifier,
    Link,
    MergedContactPointIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
    Text,
)


class BasePrimarySource(BaseModel):
    """A collection of information, that is managed and curated by an RKI unit."""

    alternativeTitle: list[Text] = []
    contact: list[
        MergedOrganizationalUnitIdentifier
        | MergedPersonIdentifier
        | MergedContactPointIdentifier
    ] = []
    description: list[Text] = []
    documentation: list[Link] = []
    locatedAt: list[Link] = []
    title: list[Text] = []
    unitInCharge: list[MergedOrganizationalUnitIdentifier] = []
    version: (
        Annotated[
            str,
            Field(
                examples=["v1", "2023-01-16", "Schema 9"],
            ),
        ]
        | None
    ) = None


class ExtractedPrimarySource(BasePrimarySource, ExtractedData):
    """An automatically extracted metadata set describing a primary source."""

    entityType: Annotated[
        Literal["ExtractedPrimarySource"], Field(alias="$type", frozen=True)
    ] = "ExtractedPrimarySource"
    identifier: Annotated[ExtractedPrimarySourceIdentifier, Field(frozen=True)]
    stableTargetId: MergedPrimarySourceIdentifier


class MergedPrimarySource(BasePrimarySource, MergedItem):
    """The result of merging all extracted data and rules for a primary source."""

    entityType: Annotated[
        Literal["MergedPrimarySource"], Field(alias="$type", frozen=True)
    ] = "MergedPrimarySource"
    identifier: Annotated[MergedPrimarySourceIdentifier, Field(frozen=True)]
