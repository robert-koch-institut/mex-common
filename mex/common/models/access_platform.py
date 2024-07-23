"""A way of physically accessing the Resource for re-use."""

from typing import Annotated, ClassVar, Literal

from pydantic import Field, computed_field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.models.rules import (
    AdditiveRule,
    PreventiveRule,
    SubtractiveRule,
)
from mex.common.types import (
    APIType,
    ExtractedAccessPlatformIdentifier,
    Link,
    MergedAccessPlatformIdentifier,
    MergedContactPointIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedPersonIdentifier,
    TechnicalAccessibility,
    Text,
)
from mex.common.types.identifier import MergedPrimarySourceIdentifier


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["AccessPlatform"], Field(frozen=True)]] = (
        "AccessPlatform"
    )


class _OptionalLists(_Stem):
    alternativeTitle: list[Text] = []
    contact: list[
        MergedOrganizationalUnitIdentifier
        | MergedPersonIdentifier
        | MergedContactPointIdentifier
    ] = []
    description: list[Text] = []
    landingPage: list[Link] = []
    title: list[Text] = []
    unitInCharge: list[MergedOrganizationalUnitIdentifier] = []


class _OptionalValues(_Stem):
    endpointDescription: Link | None = None
    endpointType: (
        Annotated[APIType, Field(examples=["https://mex.rki.de/item/api-type-1"])]
        | None
    ) = None
    endpointURL: Link | None = None


class _RequiredValues(_Stem):
    technicalAccessibility: Annotated[
        TechnicalAccessibility,
        Field(examples=["https://mex.rki.de/item/technical-accessibility-1"]),
    ]


class _SparseValues(_Stem):
    technicalAccessibility: Annotated[
        TechnicalAccessibility | None,
        Field(examples=["https://mex.rki.de/item/technical-accessibility-1"]),
    ] = None


class _VariadicValues(_Stem):
    endpointDescription: list[Link]
    endpointType: list[
        Annotated[APIType, Field(examples=["https://mex.rki.de/item/api-type-1"])]
    ] = []
    endpointURL: list[Link] = []
    technicalAccessibility: list[
        Annotated[
            TechnicalAccessibility,
            Field(examples=["https://mex.rki.de/item/technical-accessibility-1"]),
        ]
    ] = []


class BaseAccessPlatform(_OptionalLists, _OptionalValues, _RequiredValues):
    """All fields for a valid access platform except for provenance."""


class ExtractedAccessPlatform(BaseAccessPlatform, ExtractedData):
    """An automatically extracted metadata item describing an access platform."""

    entityType: Annotated[
        Literal["ExtractedAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "ExtractedAccessPlatform"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(self) -> ExtractedAccessPlatformIdentifier:
        """Return the computed identifier for this extracted data item."""
        return self._get_identifier(ExtractedAccessPlatformIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedAccessPlatformIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted data item."""
        return self._get_stable_target_id(MergedAccessPlatformIdentifier)


class MergedAccessPlatform(BaseAccessPlatform, MergedItem):
    """The result of merging all extracted data and rules for an access platform."""

    entityType: Annotated[
        Literal["MergedAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "MergedAccessPlatform"
    identifier: Annotated[MergedAccessPlatformIdentifier, Field(frozen=True)]


class AdditiveAccessPlatform(
    _OptionalLists, _OptionalValues, _SparseValues, AdditiveRule
):
    """Rule to add values to merged access platform items."""

    entityType: Annotated[
        Literal["AdditiveAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "AdditiveAccessPlatform"


class SubtractiveAccessPlatform(_OptionalLists, _VariadicValues, SubtractiveRule):
    """Rule to subtract values from merged access platform items."""

    entityType: Annotated[
        Literal["SubtractiveAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "SubtractiveAccessPlatform"


class PreventiveAccessPlatform(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged access platform items."""

    entityType: Annotated[
        Literal["PreventiveAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "PreventiveAccessPlatform"
    alternativeTitle: list[MergedPrimarySourceIdentifier] = []
    contact: list[MergedPrimarySourceIdentifier] = []
    description: list[MergedPrimarySourceIdentifier] = []
    endpointDescription: list[MergedPrimarySourceIdentifier] = []
    endpointType: list[MergedPrimarySourceIdentifier] = []
    endpointURL: list[MergedPrimarySourceIdentifier] = []
    landingPage: list[MergedPrimarySourceIdentifier] = []
    technicalAccessibility: list[MergedPrimarySourceIdentifier] = []
    title: list[MergedPrimarySourceIdentifier] = []
    unitInCharge: list[MergedPrimarySourceIdentifier] = []
