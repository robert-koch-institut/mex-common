"""An organizational unit which is part of some larger organization."""

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

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(self) -> ExtractedOrganizationalUnitIdentifier:
        """Return the computed identifier for this extracted item."""
        return self._get_identifier(ExtractedOrganizationalUnitIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedOrganizationalUnitIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted item."""
        return self._get_stable_target_id(MergedOrganizationalUnitIdentifier)


class MergedOrganizationalUnit(BaseOrganizationalUnit, MergedItem):
    """The result of merging all extracted items and rules for an organizational unit."""  # noqa: E501

    entityType: Annotated[
        Literal["MergedOrganizationalUnit"], Field(alias="$type", frozen=True)
    ] = "MergedOrganizationalUnit"
    identifier: Annotated[MergedOrganizationalUnitIdentifier, Field(frozen=True)]


class PreviewOrganizationalUnit(
    _OptionalLists, _SparseLists, _OptionalValues, PreviewItem
):
    """Preview for merging all extracted items and rules for an organizational unit."""

    entityType: Annotated[
        Literal["PreviewOrganizationalUnit"], Field(alias="$type", frozen=True)
    ] = "PreviewOrganizationalUnit"
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


class _BaseRuleSet(_Stem, RuleSet):
    additive: AdditiveOrganizationalUnit = AdditiveOrganizationalUnit()
    subtractive: SubtractiveOrganizationalUnit = SubtractiveOrganizationalUnit()
    preventive: PreventiveOrganizationalUnit = PreventiveOrganizationalUnit()


class OrganizationalUnitRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update an organizational unit item."""

    entityType: Annotated[
        Literal["OrganizationalUnitRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "OrganizationalUnitRuleSetRequest"


class OrganizationalUnitRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve an organizational unit item."""

    entityType: Annotated[
        Literal["OrganizationalUnitRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "OrganizationalUnitRuleSetResponse"
    stableTargetId: MergedOrganizationalUnitIdentifier


class OrganizationalUnitMapping(_Stem, BaseMapping):
    """Mapping for describing an organizational unit transformation."""

    entityType: Annotated[
        Literal["OrganizationalUnitMapping"], Field(alias="$type", frozen=True)
    ] = "OrganizationalUnitMapping"
    hadPrimarySource: Annotated[
        list[MappingField[MergedPrimarySourceIdentifier]], Field(min_length=1)
    ]
    identifierInPrimarySource: Annotated[list[MappingField[str]], Field(min_length=1)]
    parentUnit: list[MappingField[MergedOrganizationalUnitIdentifier | None]] = []
    name: Annotated[list[MappingField[list[Text]]], Field(min_length=1)]
    alternativeName: list[MappingField[list[Text]]] = []
    email: list[MappingField[list[Email]]] = []
    shortName: list[MappingField[list[Text]]] = []
    unitOf: list[MappingField[list[MergedOrganizationIdentifier]]] = []
    website: list[MappingField[list[Link]]] = []


class OrganizationalUnitFilter(_Stem, BaseFilter):
    """Class for defining filter rules for organizational unit items."""

    entityType: Annotated[
        Literal["OrganizationalUnitFilter"], Field(alias="$type", frozen=True)
    ] = "OrganizationalUnitFilter"
    fields: Annotated[list[FilterField], Field(title="fields")] = []
