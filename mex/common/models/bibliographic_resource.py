"""A book, article, or other documentary resource."""

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
        ]
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
        ]
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
        ]
    ),
]


class _Stem(BaseModel):
    stemType: ClassVar[
        Annotated[Literal["BibliographicResource"], Field(frozen=True)]
    ] = "BibliographicResource"


class _OptionalLists(_Stem):
    abstract: list[Text] = []
    alternateIdentifier: list[str] = []
    alternativeTitle: list[Text] = []
    bibliographicResourceType: list[BibliographicResourceType] = []
    contributingUnit: list[MergedOrganizationalUnitIdentifier] = []
    distribution: list[MergedDistributionIdentifier] = []
    editor: list[MergedPersonIdentifier] = []
    editorOfSeries: list[MergedPersonIdentifier] = []
    isbnIssn: list[IsbnIssnStr] = []
    journal: list[Text] = []
    keyword: list[Text] = []
    language: list[Language] = []
    publisher: list[MergedOrganizationIdentifier] = []
    repositoryURL: list[Link] = []
    subtitle: list[Text] = []
    titleOfBook: list[Text] = []
    titleOfSeries: list[Text] = []


class _RequiredLists(_Stem):
    creator: Annotated[list[MergedPersonIdentifier], Field(min_length=1)]
    title: Annotated[list[Text], Field(min_length=1)]


class _SparseLists(_Stem):
    creator: list[MergedPersonIdentifier] = []
    title: list[Text] = []


class _OptionalValues(_Stem):
    doi: DoiStr | None = None
    edition: EditionStr | None = None
    issue: VolumeOrIssueStr | None = None
    issued: YearMonthDayTime | YearMonthDay | YearMonth | Year | None = None
    license: License | None = None
    pages: PagesStr | None = None
    publicationPlace: PublicationPlaceStr | None = None
    publicationYear: Year | None = None
    section: SectionStr | None = None
    volume: VolumeOrIssueStr | None = None
    volumeOfSeries: VolumeOrIssueStr | None = None


class _RequiredValues(_Stem):
    accessRestriction: AccessRestriction


class _SparseValues(_Stem):
    accessRestriction: AccessRestriction | None = None


class _VariadicValues(_Stem):
    accessRestriction: list[AccessRestriction] = []
    doi: list[DoiStr] = []
    edition: list[EditionStr] = []
    issue: list[VolumeOrIssueStr] = []
    issued: list[YearMonthDayTime | YearMonthDay | YearMonth | Year] = []
    license: list[License] = []
    pages: list[PagesStr] = []
    publicationPlace: list[PublicationPlaceStr] = []
    publicationYear: list[Year] = []
    repositoryURL: list[Link] = []
    section: list[SectionStr] = []
    volume: list[VolumeOrIssueStr] = []
    volumeOfSeries: list[VolumeOrIssueStr] = []


class BaseBibliographicResource(
    _OptionalLists, _RequiredLists, _OptionalValues, _RequiredValues
):
    """All fields for a valid bibliographic resource except for provenance."""


class ExtractedBibliographicResource(BaseBibliographicResource, ExtractedData):
    """An automatically extracted metadata item describing a bibliographic resource."""

    entityType: Annotated[
        Literal["ExtractedBibliographicResource"], Field(alias="$type", frozen=True)
    ] = "ExtractedBibliographicResource"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(self) -> ExtractedBibliographicResourceIdentifier:
        """Return the computed identifier for this extracted item."""
        return self._get_identifier(ExtractedBibliographicResourceIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedBibliographicResourceIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted item."""
        return self._get_stable_target_id(MergedBibliographicResourceIdentifier)


class MergedBibliographicResource(BaseBibliographicResource, MergedItem):
    """The result of merging all extracted items and rules for a bibliographic resource."""  # noqa: E501

    entityType: Annotated[
        Literal["MergedBibliographicResource"], Field(alias="$type", frozen=True)
    ] = "MergedBibliographicResource"
    identifier: Annotated[MergedBibliographicResourceIdentifier, Field(frozen=True)]


class PreviewBibliographicResource(
    _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, PreviewItem
):
    """Preview for merging all extracted items and rules for a bibliographic resource."""  # noqa: E501

    entityType: Annotated[
        Literal["PreviewBibliographicResource"], Field(alias="$type", frozen=True)
    ] = "PreviewBibliographicResource"
    identifier: Annotated[MergedBibliographicResourceIdentifier, Field(frozen=True)]


class AdditiveBibliographicResource(
    _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, AdditiveRule
):
    """Rule to add values to merged bibliographic resource items."""

    entityType: Annotated[
        Literal["AdditiveBibliographicResource"], Field(alias="$type", frozen=True)
    ] = "AdditiveBibliographicResource"


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
    hadPrimarySource: Annotated[
        list[MappingField[MergedPrimarySourceIdentifier]], Field(min_length=1)
    ]
    identifierInPrimarySource: Annotated[list[MappingField[str]], Field(min_length=1)]
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
