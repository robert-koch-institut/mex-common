"""A collection of information, that is managed and curated by an RKI unit."""

from typing import Annotated, ClassVar, Literal

from pydantic import AfterValidator, Field, computed_field

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
    ExtractedPrimarySourceIdentifier,
    Identifier,
    Link,
    MergedContactPointIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
    Text,
)

VersionStr = Annotated[
    str,
    Field(
        examples=["v1", "2023-01-16", "Schema 9"],
    ),
]
AnyContactIdentifier = Annotated[
    MergedOrganizationalUnitIdentifier
    | MergedPersonIdentifier
    | MergedContactPointIdentifier,
    AfterValidator(Identifier),
]


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["PrimarySource"], Field(frozen=True)]] = (
        "PrimarySource"
    )


class _OptionalLists(_Stem):
    alternativeTitle: list[Text] = []
    contact: list[AnyContactIdentifier] = []
    description: list[Text] = []
    documentation: list[Link] = []
    locatedAt: list[Link] = []
    title: list[Text] = []
    unitInCharge: list[MergedOrganizationalUnitIdentifier] = []


class _OptionalValues(_Stem):
    version: VersionStr | None = None


class _VariadicValues(_Stem):
    version: list[VersionStr] = []


class BasePrimarySource(_OptionalLists, _OptionalValues):
    """All fields for a valid primary source except for provenance."""


class ExtractedPrimarySource(BasePrimarySource, ExtractedData):
    """An automatically extracted metadata set describing a primary source."""

    entityType: Annotated[
        Literal["ExtractedPrimarySource"], Field(alias="$type", frozen=True)
    ] = "ExtractedPrimarySource"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(self) -> ExtractedPrimarySourceIdentifier:
        """Return the computed identifier for this extracted item."""
        return self._get_identifier(ExtractedPrimarySourceIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedPrimarySourceIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted item."""
        return self._get_stable_target_id(MergedPrimarySourceIdentifier)


class MergedPrimarySource(BasePrimarySource, MergedItem):
    """The result of merging all extracted items and rules for a primary source."""

    entityType: Annotated[
        Literal["MergedPrimarySource"], Field(alias="$type", frozen=True)
    ] = "MergedPrimarySource"
    identifier: Annotated[MergedPrimarySourceIdentifier, Field(frozen=True)]


class PreviewPrimarySource(_OptionalLists, _OptionalValues, PreviewItem):
    """Preview for merging all extracted items and rules for a primary source."""

    entityType: Annotated[
        Literal["PreviewPrimarySource"], Field(alias="$type", frozen=True)
    ] = "PreviewPrimarySource"
    identifier: Annotated[MergedPrimarySourceIdentifier, Field(frozen=True)]


class AdditivePrimarySource(_OptionalLists, _OptionalValues, AdditiveRule):
    """Rule to add values to merged primary source items."""

    entityType: Annotated[
        Literal["AdditivePrimarySource"], Field(alias="$type", frozen=True)
    ] = "AdditivePrimarySource"


class SubtractivePrimarySource(_OptionalLists, _VariadicValues, SubtractiveRule):
    """Rule to subtract values from merged primary source items."""

    entityType: Annotated[
        Literal["SubtractivePrimarySource"], Field(alias="$type", frozen=True)
    ] = "SubtractivePrimarySource"


class PreventivePrimarySource(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged primary source items."""

    entityType: Annotated[
        Literal["PreventivePrimarySource"], Field(alias="$type", frozen=True)
    ] = "PreventivePrimarySource"
    alternativeTitle: list[MergedPrimarySourceIdentifier] = []
    contact: list[MergedPrimarySourceIdentifier] = []
    description: list[MergedPrimarySourceIdentifier] = []
    documentation: list[MergedPrimarySourceIdentifier] = []
    locatedAt: list[MergedPrimarySourceIdentifier] = []
    title: list[MergedPrimarySourceIdentifier] = []
    unitInCharge: list[MergedPrimarySourceIdentifier] = []
    version: list[MergedPrimarySourceIdentifier] = []


class _BaseRuleSet(_Stem, RuleSet):
    additive: AdditivePrimarySource = AdditivePrimarySource()
    subtractive: SubtractivePrimarySource = SubtractivePrimarySource()
    preventive: PreventivePrimarySource = PreventivePrimarySource()


class PrimarySourceRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update a primary source item."""

    entityType: Annotated[
        Literal["PrimarySourceRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "PrimarySourceRuleSetRequest"


class PrimarySourceRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve a primary source item."""

    entityType: Annotated[
        Literal["PrimarySourceRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "PrimarySourceRuleSetResponse"
    stableTargetId: MergedPrimarySourceIdentifier


class PrimarySourceMapping(_Stem, BaseMapping):
    """Mapping for describing a primary source transformation."""

    entityType: Annotated[
        Literal["PrimarySourceMapping"], Field(alias="$type", frozen=True)
    ] = "PrimarySourceMapping"
    hadPrimarySource: Annotated[
        list[MappingField[MergedPrimarySourceIdentifier]], Field(min_length=1)
    ]
    identifierInPrimarySource: Annotated[list[MappingField[str]], Field(min_length=1)]
    version: list[MappingField[VersionStr | None]] = []
    alternativeTitle: list[MappingField[list[Text]]] = []
    contact: list[MappingField[list[AnyContactIdentifier]]] = []
    description: list[MappingField[list[Text]]] = []
    documentation: list[MappingField[list[Link]]] = []
    locatedAt: list[MappingField[list[Link]]] = []
    title: list[MappingField[list[Text]]] = []
    unitInCharge: list[MappingField[list[MergedOrganizationalUnitIdentifier]]] = []


class PrimarySourceFilter(_Stem, BaseFilter):
    """Class for defining filter rules for primary source items."""

    entityType: Annotated[
        Literal["PrimarySourceFilter"], Field(alias="$type", frozen=True)
    ] = "PrimarySourceFilter"
    fields: Annotated[list[FilterField], Field(title="fields")] = []
