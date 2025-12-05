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
    AccessRestriction,
    BibliographicResourceType,
    ExtractedBibliographicResourceIdentifier,
    Language,
    License,
    Link,
    MergedBibliographicResourceIdentifier,
    MergedDistributionIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
    Text,
    Year,
    YearMonth,
    YearMonthDay,
    YearMonthDayTime,
)

DoiStr = Annotated[
    str,
    Field(
        pattern="^https?://(?:dx\\.)?doi\\.org/[0-9]{2}\\.[0-9]{4,9}[-_.;()/:A-Za-z0-9]{0,256}$",
        examples=[
            "https://doi.org/10.1007/978-1-0716-2441-8_7",
            "https://doi.org/10.2807/1560-7917.ES.2022.27.46.2200849",
            "https://doi.org/10.3389/fmicb.2022.868887",
            "http://dx.doi.org/10.25646/5147",
            "https://doi.org/10.1016/j.vaccine.2022.11.065",
        ],
    ),
]
EditionStr = Annotated[
    str,
    Field(
        examples=[
            "5",
            "Band 2,1",
            "Band 2,2",
            "3rd edition",
        ],
    ),
]
IsbnIssnStr = Annotated[
    str,
    Field(
        examples=[
            "ISBN 90-70002-34-5",
            "ISBN 90-70002-34-x",
            "ISBN 90-70002-34-5x",
            "ISBN 90-700-02-34-5",
            "ISBN: 978-3-642-11746-6",
            "978-3-642-11746-6",
            "ISSN 0176-6996",
            "ISSN 1430-855X",
            "1430-8551",
            "1467-9442",
        ],
    ),
]
PagesStr = Annotated[
    str,
    Field(
        examples=[
            "1",
            "45-67",
            "45 - 67",
            "II",
            "XI",
            "10i",
        ],
    ),
]
PublicationPlaceStr = Annotated[
    str,
    Field(
        examples=[
            "Berlin",
            "Chigago",
            "NYC/NY",
            "Tampa, FL",
        ],
    ),
]
SectionStr = Annotated[
    str,
    Field(
        examples=[
            "Kapitel 1",
            "A Section About Public Health",
            "Chapter XII: The History of Public Health",
            "12",
            "A",
            "B.",
        ],
    ),
]
VolumeOrIssueStr = Annotated[
    str,
    Field(
        examples=[
            "2",
            "Q3",
            "11/12",
            "Winter '23",
        ],
    ),
]


class _Stem(BaseModel):
    stemType: ClassVar[
        Annotated[Literal["BibliographicResource"], Field(frozen=True)]
    ] = "BibliographicResource"


class _OptionalLists(_Stem):
    abstract: Annotated[
        list[Text],
        Field(
            description="An account of the publication.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/abstract"]},
        ),
    ] = []
    alternateIdentifier: Annotated[
        list[str],
        Field(
            description="Another identifier used for the reference.",
            json_schema_extra={
                "sameAs": ["http://datacite.org/schema/kernel-4/alternateIdentifier"]
            },
        ),
    ] = []
    alternativeTitle: Annotated[
        list[Text],
        Field(
            description="Another title for the publication.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/alternative"]},
        ),
    ] = []
    bibliographicResourceType: Annotated[
        list[BibliographicResourceType],
        Field(
            description="The type of bibliographic resource.",
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/type"]},
        ),
    ] = []
    contributingUnit: Annotated[
        list[MergedOrganizationalUnitIdentifier],
        Field(
            description=(
                "An organizational unit of RKI, that is contributing to the "
                "publication."
            ),
            json_schema_extra={
                "subPropertyOf": ["http://purl.org/dc/terms/contributor"]
            },
        ),
    ] = []
    distribution: Annotated[
        list[MergedDistributionIdentifier],
        Field(
            description=(
                "An available distribution of the publication ([DCAT, 2020-02-04]"
                "(https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/))"
            ),
        ),
    ] = []
    editor: Annotated[
        list[MergedPersonIdentifier],
        Field(
            description="The editor of the publication.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/contributor"]},
        ),
    ] = []
    editorOfSeries: Annotated[
        list[MergedPersonIdentifier],
        Field(
            description="The editor of the series.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/contributor"]},
        ),
    ] = []
    isbnIssn: Annotated[
        list[IsbnIssnStr],
        Field(
            description=(
                "Either the ISBN (for books) or ISSN (for periodicals) of the "
                "publication."
            ),
            json_schema_extra={
                "sameAs": ["http://datacite.org/schema/kernel-4/alternateIdentifier"]
            },
        ),
    ] = []
    journal: Annotated[
        list[Text],
        Field(
            description="The periodical in which the article was published.",
        ),
    ] = []
    keyword: Annotated[
        list[Text],
        Field(
            description=(
                "A keyword or tag describing the resource ([DCAT, 2020-02-04]"
                "(https://www.w3.org/TR/2020/REC-vocab-dcat-2-20200204/))."
            ),
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/dcat#keyword"]},
        ),
    ] = []
    language: Annotated[
        list[Language],
        Field(
            description="The language in which the publication was written.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/language"]},
        ),
    ] = []
    publisher: Annotated[
        list[MergedOrganizationIdentifier],
        Field(
            description=(
                "An entity responsible for making the publication available "
                "([DCT, 2020-01-20](http://dublincore.org/specifications/"
                "dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={"sameAs": "http://purl.org/dc/terms/publisher"},
        ),
    ] = []
    repositoryURL: Annotated[
        list[Link],
        Field(
            description=(
                "The handle of the publication in the repository, where the "
                "publication is stored."
            ),
        ),
    ] = []
    subtitle: Annotated[
        list[Text],
        Field(
            description="The subtitle of the publication.",
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/title"]},
        ),
    ] = []
    titleOfBook: Annotated[
        list[Text],
        Field(
            description="The title of the book in which the book section is published.",
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/title"]},
        ),
    ] = []
    titleOfSeries: Annotated[
        list[Text],
        Field(
            description="The title of the book series, the book belongs to.",
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/title"]},
        ),
    ] = []


class _RequiredLists(_Stem):
    creator: Annotated[
        list[MergedPersonIdentifier],
        Field(
            description="The author of the publication.",
            min_length=1,
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/creator"]},
        ),
    ]
    title: Annotated[
        list[Text],
        Field(
            description="The full title of the publication.",
            min_length=1,
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/title"]},
        ),
    ]


class _SparseLists(_Stem):
    creator: Annotated[
        list[MergedPersonIdentifier],
        Field(description="The author of the publication."),
    ] = []
    title: Annotated[
        list[Text], Field(description="The full title of the publication.")
    ] = []


class _OptionalValues(_Stem):
    doi: Annotated[
        DoiStr | None,
        Field(description="The Digital Object Identifier (DOI) of the publication."),
    ] = None
    edition: Annotated[
        EditionStr | None, Field(description="The edition of the publication.")
    ] = None
    issue: Annotated[
        VolumeOrIssueStr | None, Field(description="The issue of the periodical.")
    ] = None
    issued: Annotated[
        YearMonthDayTime | YearMonthDay | YearMonth | Year | None,
        Field(
            description=(
                "Date of formal issuance of the publication ([DCT, 2020-01-20]"
                "(http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/created"]},
        ),
    ] = None
    license: Annotated[
        License | None,
        Field(
            description=(
                "A legal document giving official permission to do something with "
                "the publication ([DCT, 2020-01-20](http://dublincore.org/"
                "specifications/dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/license"]},
        ),
    ] = None
    pages: Annotated[
        PagesStr | None,
        Field(description="The range of pages or a single page."),
    ] = None
    publicationPlace: Annotated[
        PublicationPlaceStr | None,
        Field(description="The place where the document was issued."),
    ] = None
    publicationYear: Annotated[
        Year | None,
        Field(
            description="The year in which the publication was issued.",
            json_schema_extra={
                "sameAs": "http://datacite.org/schema/kernel-4/publicationYear"
            },
        ),
    ] = None
    section: Annotated[
        SectionStr | None,
        Field(
            description=(
                "The name of the chapter of the publication, the book section "
                "belongs to."
            )
        ),
    ] = None
    volume: Annotated[
        VolumeOrIssueStr | None,
        Field(description="The volume of the periodical."),
    ] = None
    volumeOfSeries: Annotated[
        VolumeOrIssueStr | None,
        Field(description="The volume of the periodical series."),
    ] = None


class _RequiredValues(_Stem):
    accessRestriction: Annotated[
        AccessRestriction,
        Field(
            description="Indicates how access to the publication is restricted.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/accessRights"]},
        ),
    ]


class _SparseValues(_Stem):
    accessRestriction: Annotated[
        AccessRestriction | None,
        Field(
            description="Indicates how access to the publication is restricted.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/accessRights"]},
        ),
    ] = None


class _VariadicValues(_Stem):
    accessRestriction: Annotated[
        list[AccessRestriction],
        Field(
            description="Indicates how access to the publication is restricted.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/accessRights"]},
        ),
    ] = []
    doi: Annotated[
        list[DoiStr],
        Field(description="The Digital Object Identifier (DOI) of the publication."),
    ] = []
    edition: Annotated[
        list[EditionStr], Field(description="The edition of the publication.")
    ] = []
    issue: Annotated[
        list[VolumeOrIssueStr],
        Field(description="The issue of the periodical."),
    ] = []
    issued: Annotated[
        list[YearMonthDayTime | YearMonthDay | YearMonth | Year],
        Field(
            description=(
                "Date of formal issuance of the publication ([DCT, 2020-01-20]"
                "(http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
            ),
        ),
    ] = []
    license: Annotated[
        list[License],
        Field(
            description=(
                "A legal document giving official permission to do something with "
                "the publication ([DCT, 2020-01-20](http://dublincore.org/"
                "specifications/dublin-core/dcmi-terms/2020-01-20/))."
            ),
        ),
    ] = []
    pages: Annotated[
        list[PagesStr],
        Field(description="The range of pages or a single page."),
    ] = []
    publicationPlace: Annotated[
        list[PublicationPlaceStr],
        Field(description="The place where the document was issued."),
    ] = []
    publicationYear: Annotated[
        list[Year],
        Field(description="The year in which the publication was issued."),
    ] = []
    repositoryURL: Annotated[
        list[Link],
        Field(
            description=(
                "The handle of the publication in the repository, where the "
                "publication is stored."
            )
        ),
    ] = []
    section: Annotated[
        list[SectionStr],
        Field(
            description=(
                "The name of the chapter of the publication, the book section "
                "belongs to."
            )
        ),
    ] = []
    volume: Annotated[
        list[VolumeOrIssueStr],
        Field(description="The volume of the periodical."),
    ] = []
    volumeOfSeries: Annotated[
        list[VolumeOrIssueStr],
        Field(description="The volume of the periodical series."),
    ] = []


class BaseBibliographicResource(
    _OptionalLists,
    _RequiredLists,
    _OptionalValues,
    _RequiredValues,
    json_schema_extra={
        "description": "A book, article, or other documentary resource.",
        "sameAs": ["http://purl.org/dc/terms/BibliographicResource"],
    },
):
    """All fields for a valid bibliographic resource except for provenance."""


class ExtractedBibliographicResource(BaseBibliographicResource, ExtractedData):
    """An automatically extracted metadata item describing a bibliographic resource."""

    entityType: Annotated[
        Literal["ExtractedBibliographicResource"], Field(alias="$type", frozen=True)
    ] = "ExtractedBibliographicResource"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(  # noqa: D102
        self,
    ) -> Annotated[
        ExtractedBibliographicResourceIdentifier,
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
        return self._get_identifier(ExtractedBibliographicResourceIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(  # noqa: D102, N802
        self,
    ) -> Annotated[
        MergedBibliographicResourceIdentifier,
        Field(
            description=(
                "The identifier of the merged item that this extracted item belongs to."
            )
        ),
    ]:
        return self._get_stable_target_id(MergedBibliographicResourceIdentifier)


class MergedBibliographicResource(BaseBibliographicResource, MergedItem):
    """The result of merging all extracted items and rules for a bibliographic resource."""  # noqa: E501

    entityType: Annotated[
        Literal["MergedBibliographicResource"], Field(alias="$type", frozen=True)
    ] = "MergedBibliographicResource"
    identifier: Annotated[
        MergedBibliographicResourceIdentifier,
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
        MergedBibliographicResourceIdentifier | None,
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


class PreviewBibliographicResource(
    _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, PreviewItem
):
    """Preview for merging all extracted items and rules for a bibliographic resource."""  # noqa: E501

    entityType: Annotated[
        Literal["PreviewBibliographicResource"], Field(alias="$type", frozen=True)
    ] = "PreviewBibliographicResource"
    identifier: Annotated[
        MergedBibliographicResourceIdentifier,
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
        MergedBibliographicResourceIdentifier | None,
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


class AdditiveBibliographicResource(
    _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, AdditiveRule
):
    """Rule to add values to merged bibliographic resource items."""

    entityType: Annotated[
        Literal["AdditiveBibliographicResource"], Field(alias="$type", frozen=True)
    ] = "AdditiveBibliographicResource"
    supersededBy: Annotated[
        MergedBibliographicResourceIdentifier | None,
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


class SubtractiveBibliographicResource(
    _OptionalLists, _SparseLists, _VariadicValues, SubtractiveRule
):
    """Rule to subtract values from merged bibliographic resource items."""

    entityType: Annotated[
        Literal["SubtractiveBibliographicResource"], Field(alias="$type", frozen=True)
    ] = "SubtractiveBibliographicResource"


class PreventiveBibliographicResource(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged bibliographic resource items."""  # noqa: E501

    entityType: Annotated[
        Literal["PreventiveBibliographicResource"], Field(alias="$type", frozen=True)
    ] = "PreventiveBibliographicResource"
    abstract: list[MergedPrimarySourceIdentifier] = []
    accessRestriction: list[MergedPrimarySourceIdentifier] = []
    alternateIdentifier: list[MergedPrimarySourceIdentifier] = []
    alternativeTitle: list[MergedPrimarySourceIdentifier] = []
    bibliographicResourceType: list[MergedPrimarySourceIdentifier] = []
    contributingUnit: list[MergedPrimarySourceIdentifier] = []
    creator: list[MergedPrimarySourceIdentifier] = []
    distribution: list[MergedPrimarySourceIdentifier] = []
    doi: list[MergedPrimarySourceIdentifier] = []
    edition: list[MergedPrimarySourceIdentifier] = []
    editor: list[MergedPrimarySourceIdentifier] = []
    editorOfSeries: list[MergedPrimarySourceIdentifier] = []
    isbnIssn: list[MergedPrimarySourceIdentifier] = []
    issue: list[MergedPrimarySourceIdentifier] = []
    issued: list[MergedPrimarySourceIdentifier] = []
    journal: list[MergedPrimarySourceIdentifier] = []
    keyword: list[MergedPrimarySourceIdentifier] = []
    language: list[MergedPrimarySourceIdentifier] = []
    license: list[MergedPrimarySourceIdentifier] = []
    pages: list[MergedPrimarySourceIdentifier] = []
    publicationPlace: list[MergedPrimarySourceIdentifier] = []
    publicationYear: list[MergedPrimarySourceIdentifier] = []
    publisher: list[MergedPrimarySourceIdentifier] = []
    repositoryURL: list[MergedPrimarySourceIdentifier] = []
    section: list[MergedPrimarySourceIdentifier] = []
    subtitle: list[MergedPrimarySourceIdentifier] = []
    title: list[MergedPrimarySourceIdentifier] = []
    titleOfBook: list[MergedPrimarySourceIdentifier] = []
    titleOfSeries: list[MergedPrimarySourceIdentifier] = []
    volume: list[MergedPrimarySourceIdentifier] = []
    volumeOfSeries: list[MergedPrimarySourceIdentifier] = []


class _BaseRuleSet(_Stem, RuleSet):
    """Base class for sets of rules for a bibliographic resource item."""

    additive: AdditiveBibliographicResource = AdditiveBibliographicResource()
    subtractive: SubtractiveBibliographicResource = SubtractiveBibliographicResource()
    preventive: PreventiveBibliographicResource = PreventiveBibliographicResource()


class BibliographicResourceRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update a bibliographic resource item."""

    entityType: Annotated[
        Literal["BibliographicResourceRuleSetRequest"],
        Field(alias="$type", frozen=True),
    ] = "BibliographicResourceRuleSetRequest"


class BibliographicResourceRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve a bibliographic resource item."""

    entityType: Annotated[
        Literal["BibliographicResourceRuleSetResponse"],
        Field(alias="$type", frozen=True),
    ] = "BibliographicResourceRuleSetResponse"
    stableTargetId: MergedBibliographicResourceIdentifier


class BibliographicResourceMapping(_Stem, BaseMapping):
    """Mapping for describing a bibliographic resource transformation."""

    entityType: Annotated[
        Literal["BibliographicResourceMapping"], Field(alias="$type", frozen=True)
    ] = "BibliographicResourceMapping"
    accessRestriction: Annotated[
        list[MappingField[AccessRestriction]], Field(min_length=1)
    ]
    doi: list[MappingField[DoiStr | None]] = []
    edition: list[MappingField[EditionStr | None]] = []
    issue: list[MappingField[VolumeOrIssueStr | None]] = []
    issued: list[
        MappingField[YearMonthDayTime | YearMonthDay | YearMonth | Year | None]
    ] = []
    license: list[MappingField[License | None]] = []
    pages: list[MappingField[PagesStr | None]] = []
    publicationPlace: list[MappingField[PublicationPlaceStr | None]] = []
    publicationYear: list[MappingField[Year | None]] = []
    repositoryURL: list[MappingField[Link | None]] = []
    section: list[MappingField[SectionStr | None]] = []
    volume: list[MappingField[VolumeOrIssueStr | None]] = []
    volumeOfSeries: list[MappingField[VolumeOrIssueStr | None]] = []
    creator: Annotated[
        list[MappingField[list[MergedPersonIdentifier]]], Field(min_length=1)
    ]
    title: Annotated[list[MappingField[list[Text]]], Field(min_length=1)]
    abstract: list[MappingField[list[Text]]] = []
    alternateIdentifier: list[MappingField[list[str]]] = []
    alternativeTitle: list[MappingField[list[Text]]] = []
    bibliographicResourceType: list[MappingField[list[BibliographicResourceType]]] = []
    contributingUnit: list[MappingField[list[MergedOrganizationalUnitIdentifier]]] = []
    distribution: list[MappingField[list[MergedDistributionIdentifier]]] = []
    editor: list[MappingField[list[MergedPersonIdentifier]]] = []
    editorOfSeries: list[MappingField[list[MergedPersonIdentifier]]] = []
    isbnIssn: list[MappingField[list[IsbnIssnStr]]] = []
    journal: list[MappingField[list[Text]]] = []
    keyword: list[MappingField[list[Text]]] = []
    language: list[MappingField[list[Language]]] = []
    publisher: list[MappingField[list[MergedOrganizationIdentifier]]] = []
    subtitle: list[MappingField[list[Text]]] = []
    titleOfBook: list[MappingField[list[Text]]] = []
    titleOfSeries: list[MappingField[list[Text]]] = []


class BibliographicResourceFilter(_Stem, BaseFilter):
    """Class for defining filter rules for bibliographic resource items."""

    entityType: Annotated[
        Literal["BibliographicResourceFilter"], Field(alias="$type", frozen=True)
    ] = "BibliographicResourceFilter"
    fields: Annotated[list[FilterField], Field(title="fields")] = []
