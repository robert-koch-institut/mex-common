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
    Field(
        examples=["SF-36 Version 1"],
    ),
]
DataTypeStr = Annotated[
    str,
    Field(
        examples=["integer", "string", "image", "int55", "number"],
    ),
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
    belongsTo: Annotated[
        list[MergedVariableGroupIdentifier],
        Field(
            description=(
                "The variable group, the described variable is part of. Used to "
                "group variables together, depending on how they are structured in "
                "the primary source."
            ),
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/isPartOf"]},
        ),
    ] = []
    description: Annotated[
        list[Text],
        Field(
            description=(
                "A description of the variable. How the variable is defined in "
                "the primary source."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/description"]},
        ),
    ] = []
    valueSet: Annotated[
        list[ValueSetStr],
        Field(description="A set of predefined values as given in the primary source."),
    ] = []


class _RequiredLists(_Stem):
    label: Annotated[
        list[LabelText],
        Field(
            description="The name of the variable.",
            min_length=1,
            json_schema_extra={
                "sameAs": [
                    "http://purl.org/dc/terms/title",
                    "http://www.w3.org/2000/01/rdf-schema#label",
                ]
            },
        ),
    ]
    usedIn: Annotated[
        list[MergedResourceIdentifier],
        Field(
            description="The resource, the variable is used in.",
            min_length=1,
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/isPartOf"]},
        ),
    ]


class _SparseLists(_Stem):
    label: Annotated[
        list[LabelText],
        Field(
            description="The name of the variable.",
            json_schema_extra={
                "sameAs": [
                    "http://purl.org/dc/terms/title",
                    "http://www.w3.org/2000/01/rdf-schema#label",
                ]
            },
        ),
    ] = []
    usedIn: Annotated[
        list[MergedResourceIdentifier],
        Field(
            description="The resource, the variable is used in.",
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/isPartOf"]},
        ),
    ] = []


class _OptionalValues(_Stem):
    codingSystem: Annotated[
        CodingSystemStr | None,
        Field(
            description=(
                "An established standard to which the described resource conforms "
                "([DCT, 2020-01-20](http://dublincore.org/specifications/"
                "dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={
                "sameAs": [
                    "http://purl.org/dc/terms/conformsTo",
                    "https://schema.org/codingSystem",
                ]
            },
        ),
    ] = None
    dataType: Annotated[
        DataTypeStr | None,
        Field(
            description="The defined data type of the variable.",
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/csvw#datatype"]},
        ),
    ] = None


class _VariadicValues(_Stem):
    codingSystem: Annotated[
        list[CodingSystemStr],
        Field(
            description=(
                "An established standard to which the described resource conforms "
                "([DCT, 2020-01-20](http://dublincore.org/specifications/"
                "dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={
                "sameAs": [
                    "http://purl.org/dc/terms/conformsTo",
                    "https://schema.org/codingSystem",
                ]
            },
        ),
    ] = []
    dataType: Annotated[
        list[DataTypeStr],
        Field(
            description="The defined data type of the variable.",
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/csvw#datatype"]},
        ),
    ] = []


class BaseVariable(
    _OptionalLists,
    _RequiredLists,
    _OptionalValues,
    json_schema_extra={
        "description": (
            "Variables are defined for the data-based evaluation of investigations "
            "(e.g. studies). A variable is characterized by its data type (e.g. "
            "integer, string, date) and value range. The variable can be either "
            "quantitative or qualitative, i.e. the value range can take numerical or "
            "categorical values."
        ),
    },
):
    """All fields for a valid variable except for provenance."""


class ExtractedVariable(BaseVariable, ExtractedData):
    """An automatically extracted metadata set describing a variable."""

    entityType: Annotated[
        Literal["ExtractedVariable"], Field(alias="$type", frozen=True)
    ] = "ExtractedVariable"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(  # noqa: D102
        self,
    ) -> Annotated[
        ExtractedVariableIdentifier,
        Field(
            description=(
                "An unambiguous reference to the resource within a given context. "
                "Persistent identifiers should be provided as HTTP URIs "
                "([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={
                "sameAs": ["http://purl.org/dc/elements/1.1/identifier"]
            },
        ),
    ]:
        return self._get_identifier(ExtractedVariableIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(  # noqa: D102, N802
        self,
    ) -> Annotated[
        MergedVariableIdentifier,
        Field(
            description=(
                "The identifier of the merged item that this extracted item belongs to."
            )
        ),
    ]:
        return self._get_stable_target_id(MergedVariableIdentifier)


class MergedVariable(BaseVariable, MergedItem):
    """The result of merging all extracted items and rules for a variable."""

    entityType: Annotated[
        Literal["MergedVariable"], Field(alias="$type", frozen=True)
    ] = "MergedVariable"
    identifier: Annotated[
        MergedVariableIdentifier,
        Field(
            json_schema_extra={
                "description": (
                    "An unambiguous reference to the resource within a given context. "
                    "Persistent identifiers should be provided as HTTP URIs "
                    "([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
                ),
                "readOnly": True,
                "sameAs": ["http://purl.org/dc/elements/1.1/identifier"],
            },
            frozen=True,
        ),
    ]


class PreviewVariable(_OptionalLists, _SparseLists, _OptionalValues, PreviewItem):
    """Preview for merging all extracted items and rules for a variable."""

    entityType: Annotated[
        Literal["PreviewVariable"], Field(alias="$type", frozen=True)
    ] = "PreviewVariable"
    identifier: Annotated[
        MergedVariableIdentifier,
        Field(
            json_schema_extra={
                "description": (
                    "An unambiguous reference to the resource within a given context. "
                    "Persistent identifiers should be provided as HTTP URIs "
                    "([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
                ),
                "readOnly": True,
                "sameAs": ["http://purl.org/dc/elements/1.1/identifier"],
            },
            frozen=True,
        ),
    ]


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
    """Base class for sets of rules for a variable item."""

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
