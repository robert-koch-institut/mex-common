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
    ExtractedContactPointIdentifier,
    MergedContactPointIdentifier,
    MergedPrimarySourceIdentifier,
)

EmailStr = Annotated[
    str,
    Field(
        examples=["info@rki.de"],
        pattern="^[^@ \\t\\r\\n]+@[^@ \\t\\r\\n]+\\.[^@ \\t\\r\\n]+$",
        description="The email address associated to the contact point.",
        json_schema_extra={"format": "email"},
    ),
]


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["ContactPoint"], Field(frozen=True)]] = (
        "ContactPoint"
    )


class _RequiredLists(_Stem):
    email: Annotated[
        list[EmailStr],
        Field(
            description=None,
            json_schema_extra={
                "sameAs": [
                    "http://www.w3.org/2006/vcard/ns#hasEmail",
                    "https://schema.org/email",
                ]
            },
            min_length=1,
        ),
    ]


class _SparseLists(_Stem):
    email: Annotated[
        list[EmailStr],
        Field(
            description=None,
            json_schema_extra={
                "sameAs": [
                    "http://www.w3.org/2006/vcard/ns#hasEmail",
                    "https://schema.org/email",
                ]
            },
        ),
    ] = []


class BaseContactPoint(
    _RequiredLists,
    json_schema_extra={
        "description": "A mail address, where a group of people has access to.",
        "sameAs": ["https://schema.org/ContactPoint"],
    },
):
    """All fields for a valid contact point except for provenance."""


class ExtractedContactPoint(BaseContactPoint, ExtractedData):
    """An automatically extracted metadata set describing a contact point."""

    entityType: Annotated[
        Literal["ExtractedContactPoint"], Field(alias="$type", frozen=True)
    ] = "ExtractedContactPoint"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(
        self,
    ) -> Annotated[
        ExtractedContactPointIdentifier,
        Field(
            description=None,
            json_schema_extra={
                "sameAs": ["http://purl.org/dc/elements/1.1/identifier"]
            },
        ),
    ]:
        """An unambiguous reference to the resource within a given context."""
        return self._get_identifier(ExtractedContactPointIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedContactPointIdentifier:  # noqa: N802
        """The identifier of the merged item that this extracted item belongs to."""
        return self._get_stable_target_id(MergedContactPointIdentifier)


class MergedContactPoint(
    BaseContactPoint, MergedItem, json_schema_extra={"title": "Merged Contact Point"}
):
    """The result of merging all extracted items and rules for a contact point."""

    entityType: Annotated[
        Literal["MergedContactPoint"], Field(alias="$type", frozen=True)
    ] = "MergedContactPoint"
    identifier: Annotated[MergedContactPointIdentifier, Field(frozen=True)]


class PreviewContactPoint(_SparseLists, PreviewItem):
    """Preview for merging all extracted items and rules for a contact point."""

    entityType: Annotated[
        Literal["PreviewContactPoint"], Field(alias="$type", frozen=True)
    ] = "PreviewContactPoint"
    identifier: Annotated[MergedContactPointIdentifier, Field(frozen=True)]


class AdditiveContactPoint(_SparseLists, AdditiveRule):
    """Rule to add values to merged contact point items."""

    entityType: Annotated[
        Literal["AdditiveContactPoint"], Field(alias="$type", frozen=True)
    ] = "AdditiveContactPoint"


class SubtractiveContactPoint(_SparseLists, SubtractiveRule):
    """Rule to subtract values from merged contact point items."""

    entityType: Annotated[
        Literal["SubtractiveContactPoint"], Field(alias="$type", frozen=True)
    ] = "SubtractiveContactPoint"


class PreventiveContactPoint(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged contact point items."""

    entityType: Annotated[
        Literal["PreventiveContactPoint"], Field(alias="$type", frozen=True)
    ] = "PreventiveContactPoint"
    email: list[MergedPrimarySourceIdentifier] = []


class _BaseRuleSet(_Stem, RuleSet):
    additive: AdditiveContactPoint = AdditiveContactPoint()
    subtractive: SubtractiveContactPoint = SubtractiveContactPoint()
    preventive: PreventiveContactPoint = PreventiveContactPoint()


class ContactPointRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update a contact point item."""

    entityType: Annotated[
        Literal["ContactPointRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "ContactPointRuleSetRequest"


class ContactPointRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve a contact point item."""

    entityType: Annotated[
        Literal["ContactPointRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "ContactPointRuleSetResponse"
    stableTargetId: MergedContactPointIdentifier


class ContactPointMapping(_Stem, BaseMapping):
    """Mapping for describing a contact point transformation."""

    entityType: Annotated[
        Literal["ContactPointMapping"], Field(alias="$type", frozen=True)
    ] = "ContactPointMapping"
    email: Annotated[
        list[MappingField[list[EmailStr]]], Field(description=None, min_length=1)
    ]


class ContactPointFilter(_Stem, BaseFilter):
    """Class for defining filter rules for contact point items."""

    entityType: Annotated[
        Literal["ContactPointFilter"], Field(alias="$type", frozen=True)
    ] = "ContactPointFilter"
    fields: Annotated[list[FilterField], Field(description=None, title="fields")] = []
