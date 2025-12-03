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
    containedBy: Annotated[
        list[MergedResourceIdentifier],
        Field(
            description=None,
            min_length=1,
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/isPartOf"]},
        ),
    ]
    label: Annotated[
        list[Text],
        Field(
            description=None,
            min_length=1,
            json_schema_extra={
                "sameAs": ["http://www.w3.org/2000/01/rdf-schema#label"]
            },
        ),
    ]


class _SparseLists(_Stem):
    containedBy: Annotated[
        list[MergedResourceIdentifier],
        Field(
            description=None,
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/isPartOf"]},
        ),
    ] = []
    label: Annotated[
        list[Text],
        Field(
            description=None,
            json_schema_extra={
                "sameAs": ["http://www.w3.org/2000/01/rdf-schema#label"]
            },
        ),
    ] = []


class BaseVariableGroup(
    _RequiredLists,
    json_schema_extra={
        "description": (
            "The grouping of variables according to a certain aspect, e.g. how the "
            "information is modelled in the primary source."
        ),
    },
):
    """All fields for a valid variable group except for provenance."""


class ExtractedVariableGroup(BaseVariableGroup, ExtractedData):
    """An automatically extracted metadata set describing a variable group."""

    entityType: Annotated[
        Literal["ExtractedVariableGroup"], Field(alias="$type", frozen=True)
    ] = "ExtractedVariableGroup"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(
        self,
    ) -> Annotated[
        ExtractedVariableGroupIdentifier,
        Field(
            description=None,
            json_schema_extra={
                "sameAs": ["http://purl.org/dc/elements/1.1/identifier"]
            },
        ),
    ]:
        """An unambiguous reference to the resource within a given context."""
        return self._get_identifier(ExtractedVariableGroupIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedVariableGroupIdentifier:  # noqa: N802
        """The identifier of the merged item that this extracted item belongs to."""
        return self._get_stable_target_id(MergedVariableGroupIdentifier)


class MergedVariableGroup(
    BaseVariableGroup, MergedItem, json_schema_extra={"title": "Merged Variable Group"}
):
    """The result of merging all extracted items and rules for a variable group."""

    entityType: Annotated[
        Literal["MergedVariableGroup"], Field(alias="$type", frozen=True)
    ] = "MergedVariableGroup"
    identifier: Annotated[MergedVariableGroupIdentifier, Field(frozen=True)]


class PreviewVariableGroup(_SparseLists, PreviewItem):
    """Preview for merging all extracted items and rules for a variable group."""

    entityType: Annotated[
        Literal["PreviewVariableGroup"], Field(alias="$type", frozen=True)
    ] = "PreviewVariableGroup"
    identifier: Annotated[MergedVariableGroupIdentifier, Field(frozen=True)]


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


class _BaseRuleSet(_Stem, RuleSet):
    additive: AdditiveVariableGroup = AdditiveVariableGroup()
    subtractive: SubtractiveVariableGroup = SubtractiveVariableGroup()
    preventive: PreventiveVariableGroup = PreventiveVariableGroup()


class VariableGroupRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update a variable group item."""

    entityType: Annotated[
        Literal["VariableGroupRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "VariableGroupRuleSetRequest"


class VariableGroupRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve a variable group item."""

    entityType: Annotated[
        Literal["VariableGroupRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "VariableGroupRuleSetResponse"
    stableTargetId: MergedVariableGroupIdentifier


class VariableGroupMapping(_Stem, BaseMapping):
    """Mapping for describing a variable group transformation."""

    entityType: Annotated[
        Literal["VariableGroupMapping"], Field(alias="$type", frozen=True)
    ] = "VariableGroupMapping"
    containedBy: Annotated[
        list[MappingField[list[MergedResourceIdentifier]]],
        Field(description=None, min_length=1),
    ]
    label: Annotated[
        list[MappingField[list[Text]]], Field(description=None, min_length=1)
    ]


class VariableGroupFilter(_Stem, BaseFilter):
    """Class for defining filter rules for variable group items."""

    entityType: Annotated[
        Literal["VariableGroupFilter"], Field(alias="$type", frozen=True)
    ] = "VariableGroupFilter"
    fields: Annotated[list[FilterField], Field(description=None, title="fields")] = []
