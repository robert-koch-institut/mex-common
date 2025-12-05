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
    ExtractedPersonIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
)

EmailStr = Annotated[
    str,
    Field(
        examples=["info@rki.de"],
        pattern="^[^@ \\t\\r\\n]+@[^@ \\t\\r\\n]+\\.[^@ \\t\\r\\n]+$",
        json_schema_extra={"format": "email"},
    ),
]
FamilyNameStr = Annotated[
    str,
    Field(
        examples=["Patapoutian", "Skłodowska-Curie", "Muta Maathai"],
    ),
]
FullNameStr = Annotated[
    str,
    Field(
        examples=["Juturna Felicitás", "M. Berhanu", "Keone Seong-Hyeon"],
    ),
]
GivenNameStr = Annotated[
    str,
    Field(
        examples=["Romāns", "Marie Salomea", "May-Britt"],
    ),
]
IsniIdStr = Annotated[
    str,
    Field(
        pattern="^https://isni\\.org/isni/[X0-9]{16}$",
        examples=[
            "https://isni.org/isni/0000000019240398",
            "https://isni.org/isni/0000000453907343",
            "https://isni.org/isni/0000000038086111",
        ],
        json_schema_extra={"format": "uri"},
    ),
]
OrcidIdStr = Annotated[
    str,
    Field(
        pattern="^https://orcid\\.org/[-X0-9]{9,21}$",
        examples=[
            "https://orcid.org/0000-0002-9079-593X",
            "https://orcid.org/0000-0003-2300-3928",
            "https://orcid.org/0000-0002-1335-4022",
        ],
        json_schema_extra={"format": "uri"},
    ),
]


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["Person"], Field(frozen=True)]] = "Person"


class _OptionalLists(_Stem):
    affiliation: Annotated[
        list[MergedOrganizationIdentifier],
        Field(
            description="An organization that the described person is affiliated with.",
            json_schema_extra={
                "sameAs": [
                    "https://schema.org/affiliation",
                    "http://www.wikidata.org/entity/P1416",
                ]
            },
        ),
    ] = []
    email: Annotated[
        list[EmailStr],
        Field(
            description="The email address through which the person can be contacted.",
            json_schema_extra={
                "sameAs": [
                    "http://www.w3.org/2006/vcard/ns#hasEmail",
                    "https://schema.org/email",
                ]
            },
        ),
    ] = []
    familyName: Annotated[
        list[FamilyNameStr],
        Field(
            description="The name inherited from the family.",
            json_schema_extra={
                "sameAs": [
                    "http://xmlns.com/foaf/0.1/familyName",
                    "https://schema.org/familyName",
                ]
            },
        ),
    ] = []
    fullName: Annotated[
        list[FullNameStr],
        Field(
            description=(
                "The full name of a person. Also used if the naming schema "
                "(given name and family name) does not apply to the name."
            ),
            json_schema_extra={"sameAs": ["http://xmlns.com/foaf/0.1/name"]},
        ),
    ] = []
    givenName: Annotated[
        list[GivenNameStr],
        Field(
            description="The name given to the person e.g. by their parents.",
            json_schema_extra={
                "sameAs": [
                    "http://xmlns.com/foaf/0.1/givenName",
                    "https://schema.org/givenName",
                ]
            },
        ),
    ] = []
    isniId: Annotated[
        list[IsniIdStr],
        Field(
            description=(
                "The ISNI (International Standard Name Identifier) of the person."
            ),
            json_schema_extra={"sameAs": ["http://www.wikidata.org/entity/P213"]},
        ),
    ] = []
    memberOf: Annotated[
        list[MergedOrganizationalUnitIdentifier],
        Field(
            description="Organizational unit at RKI the person is associated with.",
            json_schema_extra={
                "sameAs": [
                    "http://www.cidoc-crm.org/cidoc-crm/P107i_is_current_or_former_member_of"
                ]
            },
        ),
    ] = []
    orcidId: Annotated[
        list[OrcidIdStr],
        Field(
            description="Identifier of a person from the ORCID authority file.",
            json_schema_extra={"sameAs": ["http://www.wikidata.org/entity/P496"]},
        ),
    ] = []


class BasePerson(
    _OptionalLists,
    json_schema_extra={
        "description": (
            "A person ([FOAF, 2004-05-01](http://xmlns.com/foaf/0.1/)). This class "
            "comprises real persons who live or are assumed to have lived ([CIDOC CRM, "
            "version 7.1.1](https://cidoc-crm.org/html/cidoc_crm_v7.1.1.html))."
        ),
        "sameAs": [
            "http://www.cidoc-crm.org/cidoc-crm/E21_Person",
            "http://xmlns.com/foaf/0.1/Person",
            "http://www.w3.org/2006/vcard/ns#Individual",
        ],
    },
):
    """All fields for a valid person except for provenance."""


class ExtractedPerson(BasePerson, ExtractedData):
    """An automatically extracted metadata set describing a person."""

    entityType: Annotated[
        Literal["ExtractedPerson"], Field(alias="$type", frozen=True)
    ] = "ExtractedPerson"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(  # noqa: D102
        self,
    ) -> Annotated[
        ExtractedPersonIdentifier,
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
        return self._get_identifier(ExtractedPersonIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(  # noqa: D102, N802
        self,
    ) -> Annotated[
        MergedPersonIdentifier,
        Field(
            description=(
                "The identifier of the merged item that this extracted item belongs to."
            )
        ),
    ]:
        return self._get_stable_target_id(MergedPersonIdentifier)


class MergedPerson(BasePerson, MergedItem):
    """The result of merging all extracted items and rules for a person."""

    entityType: Annotated[
        Literal["MergedPerson"], Field(alias="$type", frozen=True)
    ] = "MergedPerson"
    identifier: Annotated[
        MergedPersonIdentifier,
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


class PreviewPerson(_OptionalLists, PreviewItem):
    """Preview for merging all extracted items and rules for a person."""

    entityType: Annotated[
        Literal["PreviewPerson"], Field(alias="$type", frozen=True)
    ] = "PreviewPerson"
    identifier: Annotated[
        MergedPersonIdentifier,
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


class AdditivePerson(_OptionalLists, AdditiveRule):
    """Rule to add values to merged person items."""

    entityType: Annotated[
        Literal["AdditivePerson"], Field(alias="$type", frozen=True)
    ] = "AdditivePerson"


class SubtractivePerson(_OptionalLists, SubtractiveRule):
    """Rule to subtract values from merged person items."""

    entityType: Annotated[
        Literal["SubtractivePerson"], Field(alias="$type", frozen=True)
    ] = "SubtractivePerson"


class PreventivePerson(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged person items."""

    entityType: Annotated[
        Literal["PreventivePerson"], Field(alias="$type", frozen=True)
    ] = "PreventivePerson"
    affiliation: list[MergedPrimarySourceIdentifier] = []
    email: list[MergedPrimarySourceIdentifier] = []
    familyName: list[MergedPrimarySourceIdentifier] = []
    fullName: list[MergedPrimarySourceIdentifier] = []
    givenName: list[MergedPrimarySourceIdentifier] = []
    isniId: list[MergedPrimarySourceIdentifier] = []
    memberOf: list[MergedPrimarySourceIdentifier] = []
    orcidId: list[MergedPrimarySourceIdentifier] = []


class _BaseRuleSet(_Stem, RuleSet):
    """Base class for sets of rules for a person item."""

    additive: AdditivePerson = AdditivePerson()
    subtractive: SubtractivePerson = SubtractivePerson()
    preventive: PreventivePerson = PreventivePerson()


class PersonRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update a person item."""

    entityType: Annotated[
        Literal["PersonRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "PersonRuleSetRequest"


class PersonRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve a person item."""

    entityType: Annotated[
        Literal["PersonRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "PersonRuleSetResponse"
    stableTargetId: MergedPersonIdentifier


class PersonMapping(_Stem, BaseMapping):
    """Mapping for describing a person transformation."""

    entityType: Annotated[
        Literal["PersonMapping"], Field(alias="$type", frozen=True)
    ] = "PersonMapping"
    affiliation: list[MappingField[list[MergedOrganizationIdentifier]]] = []
    email: list[MappingField[list[EmailStr]]] = []
    familyName: list[MappingField[list[FamilyNameStr]]] = []
    fullName: list[MappingField[list[FullNameStr]]] = []
    givenName: list[MappingField[list[GivenNameStr]]] = []
    isniId: list[MappingField[list[IsniIdStr]]] = []
    memberOf: list[MappingField[list[MergedOrganizationalUnitIdentifier]]] = []
    orcidId: list[MappingField[list[OrcidIdStr]]] = []


class PersonFilter(_Stem, BaseFilter):
    """Class for defining filter rules for person items."""

    entityType: Annotated[
        Literal["PersonFilter"], Field(alias="$type", frozen=True)
    ] = "PersonFilter"
    fields: Annotated[list[FilterField], Field(title="fields")] = []
