"""A contact point - for example, an interdepartmental project."""

from typing import Annotated, ClassVar, Literal

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
    Email,
    ExtractedContactPointIdentifier,
    MergedContactPointIdentifier,
    MergedPrimarySourceIdentifier,
)


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["ContactPoint"], Field(frozen=True)]] = (
        "ContactPoint"
    )


class _RequiredLists(_Stem):
    email: Annotated[list[Email], Field(min_length=1)]


class _SparseLists(_Stem):
    email: list[Email] = []


class BaseContactPoint(_RequiredLists):
    """All fields for a valid contact point except for provenance."""


class ExtractedContactPoint(BaseContactPoint, ExtractedData):
    """An automatically extracted metadata set describing a contact point."""

    entityType: Annotated[
        Literal["ExtractedContactPoint"], Field(alias="$type", frozen=True)
    ] = "ExtractedContactPoint"
    identifier: Annotated[ExtractedContactPointIdentifier, Field(frozen=True)]
    stableTargetId: MergedContactPointIdentifier


class MergedContactPoint(BaseContactPoint, MergedItem):
    """The result of merging all extracted data and rules for a contact point."""

    entityType: Annotated[
        Literal["MergedContactPoint"], Field(alias="$type", frozen=True)
    ] = "MergedContactPoint"
    identifier: Annotated[MergedContactPointIdentifier, Field(frozen=True)]


class AdditiveContactPoint(_SparseLists, AdditiveRule):
    """Rule to add values to merged contact point items."""

    entityType: Annotated[
        Literal["AdditiveContactPoint"], Field(alias="$type", frozen=True)
    ] = "AdditiveContactPoint"


class SubtractiveContactPoint(_SparseLists, SubtractiveRule):
    """Rule to subtract values from merged contact point items."""

    entityType: Annotated[
        Literal["SubtractiveContactPoint"], Field(alias="$type", frozen=True)
    ] = "SubtractiveContactPoint"


class PreventiveContactPoint(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged contact point items."""

    entityType: Annotated[
        Literal["PreventiveContactPoint"], Field(alias="$type", frozen=True)
    ] = "PreventiveContactPoint"
    email: list[MergedPrimarySourceIdentifier] = []
