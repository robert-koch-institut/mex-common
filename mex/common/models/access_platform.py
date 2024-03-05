from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import (
    APIType,
    ExtractedAccessPlatformIdentifier,
    Link,
    MergedAccessPlatformIdentifier,
    MergedContactPointIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedPersonIdentifier,
    TechnicalAccessibility,
    Text,
)


class BaseAccessPlatform(BaseModel):
    """A way of physically accessing the Resource for re-use."""

    alternativeTitle: list[Text] = []
    contact: list[
        MergedOrganizationalUnitIdentifier
        | MergedPersonIdentifier
        | MergedContactPointIdentifier
    ] = []
    description: list[Text] = []
    endpointDescription: Link | None = None
    endpointType: (
        Annotated[APIType, Field(examples=["https://mex.rki.de/item/api-type-1"])]
        | None
    ) = None
    endpointURL: Link | None = None
    landingPage: list[Link] = []
    technicalAccessibility: Annotated[
        TechnicalAccessibility,
        Field(examples=["https://mex.rki.de/item/technical-accessibility-1"]),
    ]
    title: list[Text] = []
    unitInCharge: list[MergedOrganizationalUnitIdentifier] = []


class ExtractedAccessPlatform(BaseAccessPlatform, ExtractedData):
    """An automatically extracted metadata set describing an access platform."""

    entityType: Annotated[
        Literal["ExtractedAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "ExtractedAccessPlatform"
    identifier: Annotated[ExtractedAccessPlatformIdentifier, Field(frozen=True)]
    stableTargetId: MergedAccessPlatformIdentifier


class MergedAccessPlatform(BaseAccessPlatform, MergedItem):
    """The result of merging all extracted data and rules for an access platform."""

    entityType: Annotated[
        Literal["MergedAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "MergedAccessPlatform"
    identifier: Annotated[MergedAccessPlatformIdentifier, Field(frozen=True)]
