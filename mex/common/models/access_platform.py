"""A way of physically accessing the Resource for re-use."""

from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.models.rules import (
    AdditiveRule,
    PreventiveRule,
    SubtractiveRule,
)
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
from mex.common.types.identifier import MergedPrimarySourceIdentifier


class _OptionalLists(BaseModel):
    """All list fields of an access platform that allow empty lists."""

    alternativeTitle: list[Text] = []
    contact: list[
        MergedOrganizationalUnitIdentifier
        | MergedPersonIdentifier
        | MergedContactPointIdentifier
    ] = []
    description: list[Text] = []
    landingPage: list[Link] = []
    title: list[Text] = []
    unitInCharge: list[MergedOrganizationalUnitIdentifier] = []


class _OptionalValues(BaseModel):
    endpointDescription: Link | None = None
    endpointType: (
        Annotated[APIType, Field(examples=["https://mex.rki.de/item/api-type-1"])]
        | None
    ) = None
    endpointURL: Link | None = None


class _RequiredValues(BaseModel):
    technicalAccessibility: Annotated[
        TechnicalAccessibility,
        Field(examples=["https://mex.rki.de/item/technical-accessibility-1"]),
    ]


class _SparseValues(BaseModel):
    technicalAccessibility: Annotated[
        TechnicalAccessibility | None,
        Field(examples=["https://mex.rki.de/item/technical-accessibility-1"]),
    ] = None


class _VariadicValues(BaseModel):
    endpointDescription: list[Link]
    endpointType: list[
        Annotated[APIType, Field(examples=["https://mex.rki.de/item/api-type-1"])]
    ] = []
    endpointURL: list[Link] = []
    technicalAccessibility: list[
        Annotated[
            TechnicalAccessibility,
            Field(examples=["https://mex.rki.de/item/technical-accessibility-1"]),
        ]
    ] = []


class BaseAccessPlatform(_OptionalLists, _OptionalValues, _RequiredValues):
    """All fields for a valid access platform except for provenance."""


class ExtractedAccessPlatform(BaseAccessPlatform, ExtractedData[ExtractedAccessPlatformIdentifier,ExtractedAccessPlatformIdentifier]):
    """An automatically extracted metadata item describing an access platform."""

    entityType: Annotated[
        Literal["ExtractedAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "ExtractedAccessPlatform"



class MergedAccessPlatform(BaseAccessPlatform, MergedItem):
    """The result of merging all extracted data and rules for an access platform."""

    entityType: Annotated[
        Literal["MergedAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "MergedAccessPlatform"
    identifier: Annotated[MergedAccessPlatformIdentifier, Field(frozen=True)]


class AdditiveAccessPlatform(
    _OptionalLists, _OptionalValues, _SparseValues, AdditiveRule
):
    """Rule to add values to merged access platform items."""

    entityType: Annotated[
        Literal["AdditiveAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "AdditiveAccessPlatform"


class SubtractiveAccessPlatform(_OptionalLists, _VariadicValues, SubtractiveRule):
    """Rule to subtract values from merged access platform items."""

    entityType: Annotated[
        Literal["SubtractiveAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "SubtractiveAccessPlatform"


class PreventiveAccessPlatform(PreventiveRule):
    """Rule to prevent primary sources for fields of merged access platform items."""

    entityType: Annotated[
        Literal["PreventiveAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "PreventiveAccessPlatform"
    alternativeTitle: list[MergedPrimarySourceIdentifier] = []
    contact: list[MergedPrimarySourceIdentifier] = []
    description: list[MergedPrimarySourceIdentifier] = []
    endpointDescription: list[MergedPrimarySourceIdentifier] = []
    endpointType: list[MergedPrimarySourceIdentifier] = []
    endpointURL: list[MergedPrimarySourceIdentifier] = []
    landingPage: list[MergedPrimarySourceIdentifier] = []
    technicalAccessibility: list[MergedPrimarySourceIdentifier] = []
    title: list[MergedPrimarySourceIdentifier] = []
    unitInCharge: list[MergedPrimarySourceIdentifier] = []
