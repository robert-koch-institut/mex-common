"""A single piece of information within a resource."""

from typing import Annotated, ClassVar, Literal

from pydantic import Field, computed_field

from mex.common.models.base.extracted_data import ExtractedData
from mex.common.models.base.filter import BaseFilter, FilterField
from mex.common.models.base.mapping import BaseMapping, MappingField
from mex.common.models.base.merged_item import MergedItem
from mex.common.models.base.model import BaseModel
from mex.common.models.base.preview_item import PreviewItem
from mex.common.models.base.rules import (
    AdditiveRule,
    PreventiveRule,
    RuleSet,
    SubtractiveRule,
)
from mex.common.types import (
    ExtractedVariableIdentifier,
    MergedPrimarySourceIdentifier,
    MergedResourceIdentifier,
    MergedVariableGroupIdentifier,
    MergedVariableIdentifier,
    Text,
)

CodingSystemStr = Annotated[
    str,
    Field(examples=["SF-36 Version 1"]),
]
DataTypeStr = Annotated[
    str,
    Field(examples=["integer", "string", "image", "int55", "number"]),
]
ValueSetStr = Annotated[
    str,
    Field(
        examples=[
            "Ja, stark eingeschränkt",
            "Ja, etwas eingeschränkt",
            "Nein, überhaupt nicht eingeschränkt",
        ],
    ),
]
LabelText = Annotated[
    Text,
    Field(
        examples=[{"language": "de", "value": "Mehrere Treppenabsätze steigen"}],
    ),
]


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["Variable"], Field(frozen=True)]] = "Variable"


class _OptionalLists(_Stem):
    belongsTo: list[MergedVariableGroupIdentifier] = []
    description: list[Text] = []
    valueSet: list[ValueSetStr] = []


class _RequiredLists(_Stem):
    label: Annotated[
        list[LabelText],
        Field(min_length=1),
    ]
    usedIn: Annotated[list[MergedResourceIdentifier], Field(min_length=1)]


class _SparseLists(_Stem):
    label: list[LabelText] = []
    usedIn: list[MergedResourceIdentifier] = []


class _OptionalValues(_Stem):
    codingSystem: CodingSystemStr | None = None
    dataType: DataTypeStr | None = None


class _VariadicValues(_Stem):
    codingSystem: list[CodingSystemStr] = []
    dataType: list[DataTypeStr] = []


class BaseVariable(_OptionalLists, _RequiredLists, _OptionalValues):
    """All fields for a valid variable except for provenance."""


class ExtractedVariable(BaseVariable, ExtractedData):
    """An automatically extracted metadata set describing a variable."""

    entityType: Annotated[
        Literal["ExtractedVariable"], Field(alias="$type", frozen=True)
    ] = "ExtractedVariable"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(self) -> ExtractedVariableIdentifier:
        """Return the computed identifier for this extracted item."""
        return self._get_identifier(ExtractedVariableIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedVariableIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted item."""
        return self._get_stable_target_id(MergedVariableIdentifier)


class MergedVariable(BaseVariable, MergedItem):
    """The result of merging all extracted items and rules for a variable."""

    entityType: Annotated[
        Literal["MergedVariable"], Field(alias="$type", frozen=True)
    ] = "MergedVariable"
    identifier: Annotated[MergedVariableIdentifier, Field(frozen=True)]


class PreviewVariable(_OptionalLists, _SparseLists, _OptionalValues, PreviewItem):
    """Preview for merging all extracted items and rules for a variable."""

    entityType: Annotated[
        Literal["PreviewVariable"], Field(alias="$type", frozen=True)
    ] = "PreviewVariable"
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


class _BaseRuleSet(_Stem, RuleSet):
    additive: AdditiveVariable = AdditiveVariable()
    subtractive: SubtractiveVariable = SubtractiveVariable()
    preventive: PreventiveVariable = PreventiveVariable()


class VariableRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update a variable item."""

    entityType: Annotated[
        Literal["VariableRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "VariableRuleSetRequest"


class VariableRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve a variable item."""

    entityType: Annotated[
        Literal["VariableRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "VariableRuleSetResponse"
    stableTargetId: MergedVariableIdentifier


class VariableMapping(_Stem, BaseMapping):
    """Mapping for describing a variable transformation."""

    entityType: Annotated[
        Literal["VariableMapping"], Field(alias="$type", frozen=True)
    ] = "VariableMapping"
    hadPrimarySource: Annotated[
        list[MappingField[MergedPrimarySourceIdentifier]], Field(min_length=1)
    ]
    identifierInPrimarySource: Annotated[list[MappingField[str]], Field(min_length=1)]
    codingSystem: list[MappingField[CodingSystemStr | None]] = []
    dataType: list[MappingField[DataTypeStr | None]] = []
    label: Annotated[list[MappingField[list[LabelText]]], Field(min_length=1)]
    usedIn: Annotated[
        list[MappingField[list[MergedResourceIdentifier]]], Field(min_length=1)
    ]
    belongsTo: list[MappingField[list[MergedVariableGroupIdentifier]]] = []
    description: list[MappingField[list[Text]]] = []
    valueSet: list[MappingField[list[ValueSetStr]]] = []


class VariableFilter(_Stem, BaseFilter):
    """Class for defining filter rules for variable items."""

    entityType: Annotated[
        Literal["VariableFilter"], Field(alias="$type", frozen=True)
    ] = "VariableFilter"
    fields: Annotated[list[FilterField], Field(title="fields")] = []
