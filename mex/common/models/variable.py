from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.models.rule_set import create_blocking_rule
from mex.common.types import (
    DataType,
    ExtractedVariableIdentifier,
    MergedResourceIdentifier,
    MergedVariableGroupIdentifier,
    MergedVariableIdentifier,
    Text,
)


class SparseVariable(BaseModel):
    """Variable model where all fields are optional."""

    belongsTo: list[MergedVariableGroupIdentifier] = []
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
    description: list[Text] = []
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


class BaseVariable(SparseVariable):
    """A single piece of information within a resource."""

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


class ExtractedVariable(BaseVariable, ExtractedData):
    """An automatically extracted metadata set describing a variable."""

    entityType: Annotated[
        Literal["ExtractedVariable"], Field(alias="$type", frozen=True)
    ] = "ExtractedVariable"
    identifier: Annotated[ExtractedVariableIdentifier, Field(frozen=True)]
    stableTargetId: MergedVariableIdentifier


class MergedVariable(BaseVariable, MergedItem):
    """The result of merging all extracted data and rules for a variable."""

    entityType: Annotated[
        Literal["MergedVariable"], Field(alias="$type", frozen=True)
    ] = "MergedVariable"
    identifier: Annotated[MergedVariableIdentifier, Field(frozen=True)]


class AdditiveVariable(SparseVariable):
    """Rule to add values to merged variable items."""

    entityType: Annotated[
        Literal["AdditiveVariable"], Field(alias="$type", frozen=True)
    ] = "AdditiveVariable"


class SubtractiveVariable(SparseVariable):
    """Rule to subtract values from merged variable items."""

    entityType: Annotated[
        Literal["SubtractiveVariable"], Field(alias="$type", frozen=True)
    ] = "SubtractiveVariable"


BlockingVariable = create_blocking_rule(
    Literal["BlockingVariable"],
    SparseVariable,
    "Rule to block primary sources for fields of merged variable items.",
)
