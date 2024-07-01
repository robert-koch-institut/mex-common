"""A book, article, or other documentary resource."""

from typing import Annotated, ClassVar, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.models.rules import AdditiveRule, PreventiveRule, SubtractiveRule
from mex.common.types import (
    AccessRestriction,
    BibliographicReferenceType,
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
    YearMonth,
    YearMonthDay,
    YearMonthDayTime,
)

DoiStr = Annotated[
    str,
    Field(
        examples=[
            "https://doi.org/10.1007/978-1-0716-2441-8_7",
            "https://doi.org/10.2807/1560-7917.ES.2022.27.46.2200849",
            "https://doi.org/10.3389/fmicb.2022.868887",
            "http://dx.doi.org/10.25646/5147",
            "https://doi.org/10.1016/j.vaccine.2022.11.065.",
        ],
        pattern=r"^(((http)|(https))://(dx.)?doi.org/)(10.\\d{4,9}/[-._;()/:A-Z0-9]+)$",
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


class _Stem(BaseModel):
    stemType: ClassVar[
        Annotated[Literal["BibliographicReference"], Field(frozen=True)]
    ] = "BibliographicReference"


class _OptionalLists(_Stem):
    abstract: list[Text] = []
    alternateIdentifier: list[str] = []
    alternativeTitle: list[Text] = []
    bibliographicReferenceType: list[
        Annotated[
            BibliographicReferenceType,
            Field(examples=["https://mex.rki.de/item/bibliographic-reference-type-1"]),
        ]
    ] = []
    contributingUnit: list[MergedOrganizationalUnitIdentifier] = []
    distribution: list[MergedDistributionIdentifier] = []
    editor: list[MergedPersonIdentifier] = []
    editorOfSeries: list[MergedPersonIdentifier] = []
    isbnIssn: list[IsbnIssnStr] = []
    journal: list[Text] = []
    keyword: list[Text] = []
    language: list[
        Annotated[Language, Field(examples=["https://mex.rki.de/item/language-1"])]
    ] = []
    publisher: list[MergedOrganizationIdentifier] = []
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
    edition: str | None = None
    issue: Annotated[int, Field(examples=["1", "2", "12"])] | None = None
    issued: YearMonthDayTime | YearMonthDay | YearMonth | None = None
    license: (
        Annotated[License, Field(examples=["https://mex.rki.de/item/license-1"])] | None
    ) = None
    pages: (
        Annotated[str, Field(examples=["1", "45-67", "45 - 67", "II", "XI", "10i"])]
        | None
    ) = None
    publicationYear: YearMonth | None = None  # should be just Year
    respositoryURL: Link | None = None
    section: SectionStr | None = None
    volume: Annotated[int, Field(examples=["24", "34", "1"])] | None = None
    volumeOfSeries: Annotated[int, Field(examples=["24", "34", "1"])] | None = None


class _RequiredValues(_Stem):
    accessRestriction: Annotated[
        AccessRestriction,
        Field(examples=["https://mex.rki.de/item/access-restriction-1"]),
    ]


class _SparseValues(_Stem):
    accessRestriction: (
        Annotated[
            AccessRestriction,
            Field(examples=["https://mex.rki.de/item/access-restriction-1"]),
        ]
        | None
    ) = None


class _VariadicValues(_Stem):
    accessRestriction: list[
        Annotated[
            AccessRestriction,
            Field(examples=["https://mex.rki.de/item/access-restriction-1"]),
        ]
    ] = []
    doi: list[DoiStr] = []
    edition: list[str] = []
    issue: list[Annotated[int, Field(examples=["1", "2", "12"])]] = []
    issued: list[YearMonthDayTime | YearMonthDay | YearMonth] = []
    license: list[
        Annotated[License, Field(examples=["https://mex.rki.de/item/license-1"])]
    ] = []
    pages: list[
        Annotated[str, Field(examples=["1", "45-67", "45 - 67", "II", "XI", "10i"])]
    ] = []
    publicationYear: list[YearMonth] = []  # should be just Year
    respositoryURL: list[Link] = []
    section: list[SectionStr] = []
    volume: list[Annotated[int, Field(examples=["24", "34", "1"])]] = []
    volumeOfSeries: list[Annotated[int, Field(examples=["24", "34", "1"])]] = []


class BaseBibliographicResource(
    _OptionalLists, _RequiredLists, _OptionalValues, _RequiredValues
):
    """All fields for a valid bibliographic resource except for provenance."""


class ExtractedBibliographicResource(BaseBibliographicResource, ExtractedData):
    """An automatically extracted metadata item describing a bibliographic resource."""

    entityType: Annotated[
        Literal["ExtractedBibliographicResource"], Field(alias="$type", frozen=True)
    ] = "ExtractedBibliographicResource"
    identifier: Annotated[ExtractedBibliographicResourceIdentifier, Field(frozen=True)]
    stableTargetId: MergedBibliographicResourceIdentifier


class MergedBibliographicResource(BaseBibliographicResource, MergedItem):
    """The result of merging all extracted data and rules for a bibliographic resource."""  # noqa: E501

    entityType: Annotated[
        Literal["MergedBibliographicResource"], Field(alias="$type", frozen=True)
    ] = "MergedBibliographicResource"
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


class PreventiveBibliographicResource(PreventiveRule):
    """Rule to prevent primary sources for fields of merged bibliographic resource items."""  # noqa: E501

    entityType: Annotated[
        Literal["PreventiveBibliographicResource"], Field(alias="$type", frozen=True)
    ] = "PreventiveBibliographicResource"
    abstract: list[MergedPrimarySourceIdentifier] = []
    accessRestriction: list[MergedPrimarySourceIdentifier] = []
    alternateIdentifier: list[MergedPrimarySourceIdentifier] = []
    alternativeTitle: list[MergedPrimarySourceIdentifier] = []
    bibliographicReferenceType: list[MergedPrimarySourceIdentifier] = []
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
    publicationYear: list[MergedPrimarySourceIdentifier] = []
    publisher: list[MergedPrimarySourceIdentifier] = []
    respositoryURL: list[MergedPrimarySourceIdentifier] = []
    section: list[MergedPrimarySourceIdentifier] = []
    subtitle: list[MergedPrimarySourceIdentifier] = []
    title: list[MergedPrimarySourceIdentifier] = []
    titleOfBook: list[MergedPrimarySourceIdentifier] = []
    titleOfSeries: list[MergedPrimarySourceIdentifier] = []
    volume: list[MergedPrimarySourceIdentifier] = []
    volumeOfSeries: list[MergedPrimarySourceIdentifier] = []
