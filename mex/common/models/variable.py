"""A single piece of information within a resource."""

from typing import Annotated, ClassVar, Literal

from pydantic import Field, computed_field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.models.rules import AdditiveRule, PreventiveRule, SubtractiveRule
from mex.common.types import (
    DataType,
    ExtractedVariableIdentifier,
    MergedPrimarySourceIdentifier,
    MergedResourceIdentifier,
    MergedVariableGroupIdentifier,
    MergedVariableIdentifier,
    Text,
)


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["Variable"], Field(frozen=True)]] = "Variable"


class _OptionalLists(_Stem):
    belongsTo: list[MergedVariableGroupIdentifier] = []
    description: list[Text] = []
    valueSet: list[
        Annotated[
            str,
            Field(
                examples=[
                    "Ja, stark eingeschränkt",
                    "Ja, etwas eingeschränkt",
                    "Nein, überhaupt nicht eingeschränkt",
                ],
            ),
        ]
    ] = []


class _RequiredLists(_Stem):
    label: Annotated[
        list[
            Annotated[
                Text,
                Field(
                    examples=[
                        {"language": "de", "value": "Mehrere Treppenabsätze steigen"}
                    ],
                ),
            ]
        ],
        Field(min_length=1),
    ]
    usedIn: Annotated[list[MergedResourceIdentifier], Field(min_length=1)]


class _SparseLists(_Stem):
    label: list[
        Annotated[
            Text,
            Field(
                examples=[
                    {"language": "de", "value": "Mehrere Treppenabsätze steigen"}
                ],
            ),
        ]
    ] = []
    usedIn: list[MergedResourceIdentifier] = []


class _OptionalValues(_Stem):
    codingSystem: (
        Annotated[
            str,
            Field(
                examples=["SF-36 Version 1"],
            ),
        ]
        | None
    ) = None
    dataType: (
        Annotated[
            DataType,
            Field(
                examples=["https://mex.rki.de/item/data-type-1"],
            ),
        ]
        | None
    ) = None


class _VariadicValues(_Stem):
    codingSystem: list[
        Annotated[
            str,
            Field(
                examples=["SF-36 Version 1"],
            ),
        ]
    ] = []
    dataType: list[
        Annotated[
            DataType,
            Field(
                examples=["https://mex.rki.de/item/data-type-1"],
            ),
        ]
    ] = []


class BaseVariable(_OptionalLists, _RequiredLists, _OptionalValues):
    """All fields for a valid variable except for provenance."""


class ExtractedVariable(BaseVariable, ExtractedData):
    """An automatically extracted metadata set describing a variable."""

    entityType: Annotated[
        Literal["ExtractedVariable"], Field(alias="$type", frozen=True)
    ] = "ExtractedVariable"

    @computed_field
    def identifier(self) -> ExtractedVariableIdentifier:
        """Return the computed identifier for this extracted data item."""
        return self._get_identifier(ExtractedVariableIdentifier)

    @identifier.setter  # type: ignore[no-redef]
    def identifier(self, obj: ExtractedVariableIdentifier) -> None:
        """Set the identifier field to its pre-determined value."""
        return self._set_identifier(obj)

    @computed_field
    def stableTargetId(self) -> MergedVariableIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted data item."""
        return self._get_stable_target_id(MergedVariableIdentifier)

    @stableTargetId.setter  # type: ignore[no-redef]
    def stableTargetId(self, obj: MergedVariableIdentifier) -> None:  # noqa: N802
        """Set the stableTargetId field to its pre-determined value."""
        return self._set_stable_target_id(obj)


class MergedVariable(BaseVariable, MergedItem):
    """The result of merging all extracted data and rules for a variable."""

    entityType: Annotated[
        Literal["MergedVariable"], Field(alias="$type", frozen=True)
    ] = "MergedVariable"
    identifier: Annotated[MergedVariableIdentifier, Field(frozen=True)]


class AdditiveVariable(_OptionalLists, _SparseLists, _OptionalValues, AdditiveRule):
    """Rule to add values to merged variable items."""

    entityType: Annotated[
        Literal["AdditiveVariable"], Field(alias="$type", frozen=True)
    ] = "AdditiveVariable"


class SubtractiveVariable(
    _OptionalLists, _SparseLists, _VariadicValues, SubtractiveRule
):
    """Rule to subtract values from merged variable items."""

    entityType: Annotated[
        Literal["SubtractiveVariable"], Field(alias="$type", frozen=True)
    ] = "SubtractiveVariable"


class PreventiveVariable(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged variable items."""

    entityType: Annotated[
        Literal["PreventiveVariable"], Field(alias="$type", frozen=True)
    ] = "PreventiveVariable"
    belongsTo: list[MergedPrimarySourceIdentifier] = []
    codingSystem: list[MergedPrimarySourceIdentifier] = []
    dataType: list[MergedPrimarySourceIdentifier] = []
    description: list[MergedPrimarySourceIdentifier] = []
    label: list[MergedPrimarySourceIdentifier] = []
    usedIn: list[MergedPrimarySourceIdentifier] = []
    valueSet: list[MergedPrimarySourceIdentifier] = []
