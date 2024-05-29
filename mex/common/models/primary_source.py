"""A collection of information, that is managed and curated by an RKI unit."""

from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.models.rules import AdditiveRule, PreventiveRule, SubtractiveRule
from mex.common.types import (
    ExtractedPrimarySourceIdentifier,
    Link,
    MergedContactPointIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
    Text,
)


class _OptionalLists(BaseModel):
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


class _OptionalValues(BaseModel):
    version: (
        Annotated[
            str,
            Field(
                examples=["v1", "2023-01-16", "Schema 9"],
            ),
        ]
        | None
    ) = None


class _VariadicValues(BaseModel):
    version: list[
        Annotated[
            str,
            Field(
                examples=["v1", "2023-01-16", "Schema 9"],
            ),
        ]
    ] = []


class BasePrimarySource(_OptionalLists, _OptionalValues):
    """All fields for a valid primary source except for provenance."""


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


class AdditivePrimarySource(_OptionalLists, _OptionalValues, AdditiveRule):
    """Rule to add values to merged primary source items."""

    entityType: Annotated[
        Literal["AdditivePrimarySource"], Field(alias="$type", frozen=True)
    ] = "AdditivePrimarySource"


class SubtractivePrimarySource(_OptionalLists, _VariadicValues, SubtractiveRule):
    """Rule to subtract values from merged primary source items."""

    entityType: Annotated[
        Literal["SubtractivePrimarySource"], Field(alias="$type", frozen=True)
    ] = "SubtractivePrimarySource"


class PreventivePrimarySource(PreventiveRule):
    """Rule to prevent primary sources for fields of merged primary source items."""

    entityType: Annotated[
        Literal["PreventivePrimarySource"], Field(alias="$type", frozen=True)
    ] = "PreventivePrimarySource"
    alternativeTitle: list[MergedPrimarySourceIdentifier] = []
    contact: list[MergedPrimarySourceIdentifier] = []
    description: list[MergedPrimarySourceIdentifier] = []
    documentation: list[MergedPrimarySourceIdentifier] = []
    locatedAt: list[MergedPrimarySourceIdentifier] = []
    title: list[MergedPrimarySourceIdentifier] = []
    unitInCharge: list[MergedPrimarySourceIdentifier] = []
    version: list[MergedPrimarySourceIdentifier] = []
