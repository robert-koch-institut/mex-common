from typing import Annotated

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import (
    DataType,
    ResourceID,
    Text,
    VariableGroupID,
    VariableID,
)


class BaseVariable(BaseModel):
    """A single piece of information within a resource."""

    stableTargetId: VariableID
    belongsTo: list[VariableGroupID] = []
    codingSystem: Annotated[
        str,
        Field(
            examples=["SF-36 Version 1"],
        ),
    ] | None = None
    dataType: Annotated[
        DataType,
        Field(
            examples=["https://mex.rki.de/item/data-type-1"],
        ),
    ] | None = None
    description: list[Text] = []
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
    usedIn: Annotated[list[ResourceID], Field(min_length=1)]
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


class ExtractedVariable(BaseVariable, ExtractedData):
    """An automatically extracted metadata set describing a variable."""


class MergedVariable(BaseVariable, MergedItem):
    """The result of merging all extracted data and rules for a variable."""
