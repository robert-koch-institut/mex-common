"""The grouping of variables according to a certain aspect."""

from typing import Annotated, ClassVar, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.models.rules import AdditiveRule, PreventiveRule, SubtractiveRule
from mex.common.types import (
    ExtractedVariableGroupIdentifier,
    MergedPrimarySourceIdentifier,
    MergedResourceIdentifier,
    MergedVariableGroupIdentifier,
    Text,
)


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["VariableGroup"], Field(frozen=True)]] = (
        "VariableGroup"
    )


class _RequiredLists(_Stem):
    containedBy: Annotated[list[MergedResourceIdentifier], Field(min_length=1)]
    label: Annotated[list[Text], Field(min_length=1)]


class _SparseLists(_Stem):
    containedBy: list[MergedResourceIdentifier] = []
    label: list[Text] = []


class BaseVariableGroup(_RequiredLists):
    """All fields for a valid variable group except for provenance."""


class ExtractedVariableGroup(
    BaseVariableGroup,
    ExtractedData[ExtractedVariableGroupIdentifier, MergedVariableGroupIdentifier],
):
    """An automatically extracted metadata set describing a variable group."""

    entityType: Annotated[
        Literal["ExtractedVariableGroup"], Field(alias="$type", frozen=True)
    ] = "ExtractedVariableGroup"


class MergedVariableGroup(BaseVariableGroup, MergedItem[MergedVariableGroupIdentifier]):
    """The result of merging all extracted data and rules for a variable group."""

    entityType: Annotated[
        Literal["MergedVariableGroup"], Field(alias="$type", frozen=True)
    ] = "MergedVariableGroup"


class AdditiveVariableGroup(_SparseLists, AdditiveRule):
    """Rule to add values to merged variable group items."""

    entityType: Annotated[
        Literal["AdditiveVariableGroup"], Field(alias="$type", frozen=True)
    ] = "AdditiveVariableGroup"


class SubtractiveVariableGroup(_SparseLists, SubtractiveRule):
    """Rule to subtract values from merged variable group items."""

    entityType: Annotated[
        Literal["SubtractiveVariableGroup"], Field(alias="$type", frozen=True)
    ] = "SubtractiveVariableGroup"


class PreventiveVariableGroup(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged variable group items."""

    entityType: Annotated[
        Literal["PreventiveVariableGroup"], Field(alias="$type", frozen=True)
    ] = "PreventiveVariableGroup"
    containedBy: list[MergedPrimarySourceIdentifier] = []
    label: list[MergedPrimarySourceIdentifier] = []
