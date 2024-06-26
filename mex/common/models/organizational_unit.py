"""An organizational unit which is part of some larger organization."""

from typing import Annotated, ClassVar, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.models.rules import AdditiveRule, PreventiveRule, SubtractiveRule
from mex.common.types import (
    Email,
    ExtractedOrganizationalUnitIdentifier,
    Link,
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    MergedPrimarySourceIdentifier,
    Text,
)


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["OrganizationalUnit"], Field(frozen=True)]] = (
        "OrganizationalUnit"
    )


class _OptionalLists(_Stem):
    alternativeName: list[Text] = []
    email: list[Email] = []
    shortName: list[Text] = []
    unitOf: list[MergedOrganizationIdentifier] = []
    website: list[Link] = []


class _RequiredLists(_Stem):
    name: Annotated[list[Text], Field(min_length=1)]


class _SparseLists(_Stem):
    name: list[Text] = []


class _OptionalValues(_Stem):
    parentUnit: MergedOrganizationalUnitIdentifier | None = None


class _VariadicValues(_Stem):
    parentUnit: list[MergedOrganizationalUnitIdentifier] = []


class BaseOrganizationalUnit(_OptionalLists, _RequiredLists, _OptionalValues):
    """All fields for a valid organizational unit except for provenance."""


class ExtractedOrganizationalUnit(BaseOrganizationalUnit, ExtractedData):
    """An automatically extracted metadata set describing an organizational unit."""

    entityType: Annotated[
        Literal["ExtractedOrganizationalUnit"], Field(alias="$type", frozen=True)
    ] = "ExtractedOrganizationalUnit"
    identifier: Annotated[ExtractedOrganizationalUnitIdentifier, Field(frozen=True)]
    stableTargetId: MergedOrganizationalUnitIdentifier


class MergedOrganizationalUnit(BaseOrganizationalUnit, MergedItem):
    """The result of merging all extracted data and rules for an organizational unit."""

    entityType: Annotated[
        Literal["MergedOrganizationalUnit"], Field(alias="$type", frozen=True)
    ] = "MergedOrganizationalUnit"
    identifier: Annotated[MergedOrganizationalUnitIdentifier, Field(frozen=True)]


class AdditiveOrganizationalUnit(
    _OptionalLists, _SparseLists, _OptionalValues, AdditiveRule
):
    """Rule to add values to merged organizational units."""

    entityType: Annotated[
        Literal["AdditiveOrganizationalUnit"], Field(alias="$type", frozen=True)
    ] = "AdditiveOrganizationalUnit"


class SubtractiveOrganizationalUnit(
    _OptionalLists, _SparseLists, _VariadicValues, SubtractiveRule
):
    """Rule to subtract values from merged organizational units."""

    entityType: Annotated[
        Literal["SubtractiveOrganizationalUnit"], Field(alias="$type", frozen=True)
    ] = "SubtractiveOrganizationalUnit"


class PreventiveOrganizationalUnit(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged organizational units."""

    entityType: Annotated[
        Literal["PreventiveOrganizationalUnit"], Field(alias="$type", frozen=True)
    ] = "PreventiveOrganizationalUnit"
    alternativeName: list[MergedPrimarySourceIdentifier] = []
    email: list[MergedPrimarySourceIdentifier] = []
    name: list[MergedPrimarySourceIdentifier] = []
    parentUnit: list[MergedPrimarySourceIdentifier] = []
    shortName: list[MergedPrimarySourceIdentifier] = []
    unitOf: list[MergedPrimarySourceIdentifier] = []
    website: list[MergedPrimarySourceIdentifier] = []
