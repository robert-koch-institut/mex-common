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
    ExtractedOrganizationIdentifier,
    MergedOrganizationIdentifier,
    MergedPrimarySourceIdentifier,
    Text,
)

GeprisIdStr = Annotated[
    str,
    Field(
        pattern="^https://gepris\\.dfg\\.de/gepris/institution/[0-9]{1,64}$",
        examples=[
            "https://gepris.dfg.de/gepris/institution/10179",
            "https://gepris.dfg.de/gepris/institution/10293",
            "https://gepris.dfg.de/gepris/institution/21091092",
        ],
        json_schema_extra={"format": "uri"},
    ),
]
GndIdStr = Annotated[
    str,
    Field(
        pattern="^https://d-nb\\.info/gnd/[-X0-9]{3,10}$",
        examples=[
            "https://d-nb.info/gnd/17690-4",
            "https://d-nb.info/gnd/4017909-6",
            "https://d-nb.info/gnd/4603236-8",
        ],
        json_schema_extra={"format": "uri"},
    ),
]
IsniIdStr = Annotated[
    str,
    Field(
        pattern="^https://isni\\.org/isni/[X0-9]{16}$",
        examples=[
            "https://isni.org/isni/0000000109403744",
            "https://isni.org/isni/0000000417918889",
            "https://isni.org/isni/0000000459040795",
        ],
        json_schema_extra={"format": "uri"},
    ),
]
RorIdStr = Annotated[
    str,
    Field(
        pattern="^https://ror\\.org/[a-z0-9]{9}$",
        examples=[
            "https://ror.org/01k5qnb77",
            "https://ror.org/00s9v1h75",
            "https://ror.org/04t3en479",
        ],
        json_schema_extra={"format": "uri"},
    ),
]
ViafIdStr = Annotated[
    str,
    Field(
        pattern="^https://viaf\\.org/viaf/[0-9]{2,22}$",
        examples=[
            "https://viaf.org/viaf/123556639",
            "https://viaf.org/viaf/137080884",
            "https://viaf.org/viaf/122203699",
        ],
        json_schema_extra={"format": "uri"},
    ),
]
WikidataIdStr = Annotated[
    str,
    Field(
        pattern="^http://www\\.wikidata\\.org/entity/[PQ0-9]{2,64}$",
        examples=[
            "http://www.wikidata.org/entity/Q679041",
            "http://www.wikidata.org/entity/Q918501",
            "http://www.wikidata.org/entity/Q491566",
        ],
        json_schema_extra={"format": "uri"},
    ),
]


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["Organization"], Field(frozen=True)]] = (
        "Organization"
    )


class _OptionalLists(_Stem):
    alternativeName: Annotated[
        list[Text],
        Field(
            description="An alternative name for the organization",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/alternative"]},
        ),
    ] = []
    geprisId: Annotated[
        list[GeprisIdStr],
        Field(
            description="Identifier from GEPRIS authority file.",
            json_schema_extra={"sameAs": ["http://www.wikidata.org/entity/P4871"]},
        ),
    ] = []
    gndId: Annotated[
        list[GndIdStr],
        Field(
            description=(
                "An identifier from the German authority file named Gemeinsame "
                "Normdatei (GND), curated by the German National Library (DNB)."
            ),
            json_schema_extra={"sameAs": ["http://www.wikidata.org/entity/P227"]},
        ),
    ] = []
    isniId: Annotated[
        list[IsniIdStr],
        Field(
            description=(
                "The ISNI (International Standard Name Identifier) of the organization."
            ),
            json_schema_extra={"sameAs": ["http://www.wikidata.org/entity/P213"]},
        ),
    ] = []
    rorId: Annotated[
        list[RorIdStr],
        Field(
            description="An identifier of the Research Organization Registry (ROR).",
            json_schema_extra={"sameAs": ["http://www.wikidata.org/entity/P6782"]},
        ),
    ] = []
    shortName: Annotated[
        list[Text],
        Field(
            description="A short name or abbreviation of the organization.",
            json_schema_extra={"sameAs": ["http://www.wikidata.org/entity/P1813"]},
        ),
    ] = []
    viafId: Annotated[
        list[ViafIdStr],
        Field(
            description="Identifier from VIAF (Virtual Authority File).",
            json_schema_extra={"sameAs": ["http://www.wikidata.org/entity/P214"]},
        ),
    ] = []
    wikidataId: Annotated[
        list[WikidataIdStr],
        Field(description="Identifier from Wikidata."),
    ] = []


class _RequiredLists(_Stem):
    officialName: Annotated[
        list[Text],
        Field(
            description="The official name of the organization.",
            min_length=1,
            json_schema_extra={"sameAs": ["http://www.wikidata.org/entity/P1448"]},
        ),
    ]


class _SparseLists(_Stem):
    officialName: Annotated[
        list[Text],
        Field(
            description="The official name of the organization.",
            json_schema_extra={"sameAs": ["http://www.wikidata.org/entity/P1448"]},
        ),
    ] = []


class BaseOrganization(
    _OptionalLists,
    _RequiredLists,
    json_schema_extra={
        "description": (
            "Represents a collection of people organized together into a community or "
            "other social, commercial or political structure. The group has some "
            "common purpose or reason for existence which goes beyond the set of "
            "people belonging to it and can act as an Agent. Organizations are often "
            "decomposable into hierarchical structures ([The Organization Ontology, "
            "2014-01-16](http://www.w3.org/TR/2014/REC-vocab-org-20140116/))."
        ),
        "sameAs": [
            "http://www.w3.org/ns/org#Organization",
            "http://xmlns.com/foaf/0.1/Organization",
            "http://www.w3.org/2006/vcard/ns#Organization",
            "http://www.wikidata.org/entity/Q43229",
        ],
    },
):
    """All fields for a valid organization except for provenance."""


class ExtractedOrganization(BaseOrganization, ExtractedData):
    """An automatically extracted metadata set describing an organization."""

    entityType: Annotated[
        Literal["ExtractedOrganization"], Field(alias="$type", frozen=True)
    ] = "ExtractedOrganization"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(  # noqa: D102
        self,
    ) -> Annotated[
        ExtractedOrganizationIdentifier,
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
        return self._get_identifier(ExtractedOrganizationIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(  # noqa: D102, N802
        self,
    ) -> Annotated[
        MergedOrganizationIdentifier,
        Field(
            description=(
                "The identifier of the merged item that this extracted item belongs to."
            )
        ),
    ]:
        return self._get_stable_target_id(MergedOrganizationIdentifier)


class MergedOrganization(BaseOrganization, MergedItem):
    """The result of merging all extracted items and rules for an organization."""

    entityType: Annotated[
        Literal["MergedOrganization"], Field(alias="$type", frozen=True)
    ] = "MergedOrganization"
    identifier: Annotated[
        MergedOrganizationIdentifier,
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
        MergedOrganizationIdentifier | None,
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


class PreviewOrganization(_OptionalLists, _SparseLists, PreviewItem):
    """Preview for merging all extracted items and rules for an organization."""

    entityType: Annotated[
        Literal["PreviewOrganization"], Field(alias="$type", frozen=True)
    ] = "PreviewOrganization"
    identifier: Annotated[
        MergedOrganizationIdentifier,
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
        MergedOrganizationIdentifier | None,
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


class AdditiveOrganization(_OptionalLists, _SparseLists, AdditiveRule):
    """Rule to add values to merged organization items."""

    entityType: Annotated[
        Literal["AdditiveOrganization"], Field(alias="$type", frozen=True)
    ] = "AdditiveOrganization"
    supersededBy: Annotated[
        MergedOrganizationIdentifier | None,
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


class SubtractiveOrganization(_OptionalLists, _SparseLists, SubtractiveRule):
    """Rule to subtract values from merged organization items."""

    entityType: Annotated[
        Literal["SubtractiveOrganization"], Field(alias="$type", frozen=True)
    ] = "SubtractiveOrganization"


class PreventiveOrganization(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged organization items."""

    entityType: Annotated[
        Literal["PreventiveOrganization"], Field(alias="$type", frozen=True)
    ] = "PreventiveOrganization"
    alternativeName: list[MergedPrimarySourceIdentifier] = []
    geprisId: list[MergedPrimarySourceIdentifier] = []
    gndId: list[MergedPrimarySourceIdentifier] = []
    isniId: list[MergedPrimarySourceIdentifier] = []
    officialName: list[MergedPrimarySourceIdentifier] = []
    rorId: list[MergedPrimarySourceIdentifier] = []
    shortName: list[MergedPrimarySourceIdentifier] = []
    viafId: list[MergedPrimarySourceIdentifier] = []
    wikidataId: list[MergedPrimarySourceIdentifier] = []


class _BaseRuleSet(_Stem, RuleSet):
    """Base class for sets of rules for an organization item."""

    additive: AdditiveOrganization = AdditiveOrganization()
    subtractive: SubtractiveOrganization = SubtractiveOrganization()
    preventive: PreventiveOrganization = PreventiveOrganization()


class OrganizationRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update an organization item."""

    entityType: Annotated[
        Literal["OrganizationRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "OrganizationRuleSetRequest"


class OrganizationRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve an organization item."""

    entityType: Annotated[
        Literal["OrganizationRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "OrganizationRuleSetResponse"
    stableTargetId: MergedOrganizationIdentifier


class OrganizationMapping(_Stem, BaseMapping):
    """Mapping for describing an organization transformation."""

    entityType: Annotated[
        Literal["OrganizationMapping"], Field(alias="$type", frozen=True)
    ] = "OrganizationMapping"
    officialName: Annotated[list[MappingField[list[Text]]], Field(min_length=1)]
    alternativeName: list[MappingField[list[Text]]] = []
    geprisId: list[MappingField[list[GeprisIdStr]]] = []
    gndId: list[MappingField[list[GndIdStr]]] = []
    isniId: list[MappingField[list[IsniIdStr]]] = []
    rorId: list[MappingField[list[RorIdStr]]] = []
    shortName: list[MappingField[list[Text]]] = []
    viafId: list[MappingField[list[ViafIdStr]]] = []
    wikidataId: list[MappingField[list[WikidataIdStr]]] = []


class OrganizationFilter(_Stem, BaseFilter):
    """Class for defining filter rules for organization items."""

    entityType: Annotated[
        Literal["OrganizationFilter"], Field(alias="$type", frozen=True)
    ] = "OrganizationFilter"
    fields: Annotated[list[FilterField], Field(title="fields")] = []
