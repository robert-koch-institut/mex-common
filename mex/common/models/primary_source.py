"""A collection of information, that is managed and curated by an RKI unit."""

from typing import Annotated, ClassVar, Literal

from pydantic import AfterValidator, Field, computed_field

from mex.common.models.base.extracted_data import ExtractedData
from mex.common.models.base.merged_item import MergedItem
from mex.common.models.base.model import BaseModel
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


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["PrimarySource"], Field(frozen=True)]] = (
        "PrimarySource"
    )


class _OptionalLists(_Stem):
    alternativeTitle: list[Text] = []
    contact: list[
        Annotated[
            MergedOrganizationalUnitIdentifier
            | MergedPersonIdentifier
            | MergedContactPointIdentifier,
            AfterValidator(Identifier),
        ]
    ] = []
    description: list[Text] = []
    documentation: list[Link] = []
    locatedAt: list[Link] = []
    title: list[Text] = []
    unitInCharge: list[MergedOrganizationalUnitIdentifier] = []


class _OptionalValues(_Stem):
    version: (
        Annotated[
            str,
            Field(
                examples=["v1", "2023-01-16", "Schema 9"],
            ),
        ]
        | None
    ) = None


class _VariadicValues(_Stem):
    version: list[
        Annotated[
            str,
            Field(
                examples=["v1", "2023-01-16", "Schema 9"],
            ),
        ]
    ] = []


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
        """Return the computed identifier for this extracted data item."""
        return self._get_identifier(ExtractedPrimarySourceIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedPrimarySourceIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted data item."""
        return self._get_stable_target_id(MergedPrimarySourceIdentifier)


class MergedPrimarySource(BasePrimarySource, MergedItem):
    """The result of merging all extracted data and rules for a primary source."""

    entityType: Annotated[
        Literal["MergedPrimarySource"], Field(alias="$type", frozen=True)
    ] = "MergedPrimarySource"
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
    additive: AdditivePrimarySource
    subtractive: SubtractivePrimarySource
    preventive: PreventivePrimarySource


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
