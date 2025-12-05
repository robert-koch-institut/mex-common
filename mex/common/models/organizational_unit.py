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
    ExtractedOrganizationalUnitIdentifier,
    Link,
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    MergedPrimarySourceIdentifier,
    Text,
)

EmailStr = Annotated[
    str,
    Field(
        examples=["info@rki.de"],
        pattern="^[^@ \\t\\r\\n]+@[^@ \\t\\r\\n]+\\.[^@ \\t\\r\\n]+$",
        json_schema_extra={"format": "email"},
    ),
]


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["OrganizationalUnit"], Field(frozen=True)]] = (
        "OrganizationalUnit"
    )


class _OptionalLists(_Stem):
    alternativeName: Annotated[
        list[Text],
        Field(
            description="An alternative name for the organizational unit.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/alternative"]},
        ),
    ] = []
    email: Annotated[
        list[EmailStr],
        Field(
            description=(
                "The email address through which the organizational unit can be "
                "contacted."
            ),
            json_schema_extra={
                "sameAs": [
                    "http://www.w3.org/2006/vcard/ns#hasEmail",
                    "https://schema.org/email",
                ]
            },
        ),
    ] = []
    shortName: Annotated[
        list[Text],
        Field(
            description="A short name or abbreviation of the organization unit.",
            json_schema_extra={"sameAs": ["http://www.wikidata.org/entity/P1813"]},
        ),
    ] = []
    unitOf: Annotated[
        list[MergedOrganizationIdentifier],
        Field(
            description=(
                "Indicates an organization of which this unit is a part, e.g. a "
                "department within a larger organization."
            ),
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/org#unitOf"]},
        ),
    ] = []
    website: Annotated[
        list[Link],
        Field(
            description=(
                "A URL serving as the official web presentation of the "
                "organizational unit."
            ),
            json_schema_extra={
                "sameAs": [
                    "http://www.wikidata.org/entity/P856",
                    "http://www.w3.org/2006/vcard/ns#hasUrl",
                    "http://xmlns.com/foaf/0.1/homepage",
                ]
            },
        ),
    ] = []


class _RequiredLists(_Stem):
    name: Annotated[
        list[Text],
        Field(
            description="The official name of the organizational unit.",
            min_length=1,
            json_schema_extra={"sameAs": "http://xmlns.com/foaf/0.1/name"},
        ),
    ]


class _SparseLists(_Stem):
    name: Annotated[
        list[Text],
        Field(
            description="The official name of the organizational unit.",
            json_schema_extra={"sameAs": "http://xmlns.com/foaf/0.1/name"},
        ),
    ] = []


class _OptionalValues(_Stem):
    parentUnit: Annotated[
        MergedOrganizationalUnitIdentifier | None,
        Field(
            description=(
                "The described unit is a subunit of another organizational unit."
            )
        ),
    ] = None


class _VariadicValues(_Stem):
    parentUnit: Annotated[
        list[MergedOrganizationalUnitIdentifier],
        Field(
            description=(
                "The described unit is a subunit of another organizational unit."
            )
        ),
    ] = []


class BaseOrganizationalUnit(
    _OptionalLists,
    _RequiredLists,
    _OptionalValues,
    json_schema_extra={
        "description": (
            "An Organization such as a department or support unit which is part of "
            "some larger Organization and only has full recognition within the context "
            "of that Organization. In particular the unit would not be regarded as a "
            "legal entity in its own right."
        ),
        "sameAs": [
            "http://www.w3.org/ns/org#OrganizationalUnit",
            "http://www.w3.org/2006/vcard/ns#Group",
            "http://www.cidoc-crm.org/cidoc-crm/E_74_Group",
        ],
    },
):
    """All fields for a valid organizational unit except for provenance."""


class ExtractedOrganizationalUnit(BaseOrganizationalUnit, ExtractedData):
    """An automatically extracted metadata set describing an organizational unit."""

    entityType: Annotated[
        Literal["ExtractedOrganizationalUnit"], Field(alias="$type", frozen=True)
    ] = "ExtractedOrganizationalUnit"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(  # noqa: D102
        self,
    ) -> Annotated[
        ExtractedOrganizationalUnitIdentifier,
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
        return self._get_identifier(ExtractedOrganizationalUnitIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(  # noqa: D102, N802
        self,
    ) -> Annotated[
        MergedOrganizationalUnitIdentifier,
        Field(
            description=(
                "The identifier of the merged item that this extracted item belongs to."
            )
        ),
    ]:
        return self._get_stable_target_id(MergedOrganizationalUnitIdentifier)


class MergedOrganizationalUnit(BaseOrganizationalUnit, MergedItem):
    """The result of merging all extracted items and rules for an organizational unit."""  # noqa: E501

    entityType: Annotated[
        Literal["MergedOrganizationalUnit"], Field(alias="$type", frozen=True)
    ] = "MergedOrganizationalUnit"
    identifier: Annotated[
        MergedOrganizationalUnitIdentifier,
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
    supersededBy: Annotated[
        MergedOrganizationalUnitIdentifier | None,
        Field(
            json_schema_extra={
                "description": (
                    "A merged item which is the preferred duplicate, because it "
                    "replaces, consolidates or otherwise makes the current merged item "
                    "obsolete."
                ),
            }
        ),
    ] = None


class PreviewOrganizationalUnit(
    _OptionalLists, _SparseLists, _OptionalValues, PreviewItem
):
    """Preview for merging all extracted items and rules for an organizational unit."""

    entityType: Annotated[
        Literal["PreviewOrganizationalUnit"], Field(alias="$type", frozen=True)
    ] = "PreviewOrganizationalUnit"
    identifier: Annotated[
        MergedOrganizationalUnitIdentifier,
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
    supersededBy: Annotated[
        MergedOrganizationalUnitIdentifier | None,
        Field(
            json_schema_extra={
                "description": (
                    "A merged item which is the preferred duplicate, because it "
                    "replaces, consolidates or otherwise makes the current merged item "
                    "obsolete."
                ),
            }
        ),
    ] = None


class AdditiveOrganizationalUnit(
    _OptionalLists, _SparseLists, _OptionalValues, AdditiveRule
):
    """Rule to add values to merged organizational units."""

    entityType: Annotated[
        Literal["AdditiveOrganizationalUnit"], Field(alias="$type", frozen=True)
    ] = "AdditiveOrganizationalUnit"
    supersededBy: Annotated[
        MergedOrganizationalUnitIdentifier | None,
        Field(
            json_schema_extra={
                "description": (
                    "A merged item which is the preferred duplicate, because it "
                    "replaces, consolidates or otherwise makes the current merged item "
                    "obsolete."
                ),
            }
        ),
    ] = None


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
    """Base class for sets of rules for an organizational unit item."""

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
    parentUnit: list[MappingField[MergedOrganizationalUnitIdentifier | None]] = []
    name: Annotated[list[MappingField[list[Text]]], Field(min_length=1)]
    alternativeName: list[MappingField[list[Text]]] = []
    email: list[MappingField[list[EmailStr]]] = []
    shortName: list[MappingField[list[Text]]] = []
    unitOf: list[MappingField[list[MergedOrganizationIdentifier]]] = []
    website: list[MappingField[list[Link]]] = []


class OrganizationalUnitFilter(_Stem, BaseFilter):
    """Class for defining filter rules for organizational unit items."""

    entityType: Annotated[
        Literal["OrganizationalUnitFilter"], Field(alias="$type", frozen=True)
    ] = "OrganizationalUnitFilter"
    fields: Annotated[list[FilterField], Field(title="fields")] = []
