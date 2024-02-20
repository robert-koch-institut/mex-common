from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import (
    AccessRestriction,
    ExtractedDistributionIdentifier,
    License,
    Link,
    MergedAccessPlatformIdentifier,
    MergedDistributionIdentifier,
    MergedOrganizationIdentifier,
    MergedPersonIdentifier,
    MIMEType,
    Timestamp,
)


class BaseDistribution(BaseModel):
    """A specific representation of a dataset."""

    accessService: MergedAccessPlatformIdentifier | None = None
    accessRestriction: Annotated[
        AccessRestriction,
        Field(examples=["https://mex.rki.de/item/access-restriction-1"]),
    ]
    accessURL: Link | None = None
    author: list[MergedPersonIdentifier] = []
    contactPerson: list[MergedPersonIdentifier] = []
    dataCurator: list[MergedPersonIdentifier] = []
    dataManager: list[MergedPersonIdentifier] = []
    downloadURL: Link | None = None
    issued: Timestamp
    license: (
        Annotated[License, Field(examples=["https://mex.rki.de/item/license-1"])] | None
    ) = None
    mediaType: (
        Annotated[
            MIMEType,
            Field(
                examples=["https://mex.rki.de/item/mime-type-1"],
            ),
        ]
        | None
    ) = None
    modified: Timestamp | None = None
    otherContributor: list[MergedPersonIdentifier] = []
    projectLeader: list[MergedPersonIdentifier] = []
    projectManager: list[MergedPersonIdentifier] = []
    publisher: Annotated[list[MergedOrganizationIdentifier], Field(min_length=1)]
    researcher: list[MergedPersonIdentifier] = []
    title: Annotated[
        str,
        Field(
            examples=["theNameOfTheFile"],
            min_length=1,
        ),
    ]


class ExtractedDistribution(BaseDistribution, ExtractedData):
    """An automatically extracted metadata set describing a distribution."""

    entityType: Literal["ExtractedDistribution"] = Field(
        "ExtractedDistribution", alias="$type", frozen=True
    )
    identifier: Annotated[ExtractedDistributionIdentifier, Field(frozen=True)]
    stableTargetId: MergedDistributionIdentifier


class MergedDistribution(BaseDistribution, MergedItem):
    """The result of merging all extracted data and rules for a distribution."""

    entityType: Literal["MergedDistribution"] = Field(
        "MergedDistribution", alias="$type", frozen=True
    )
    identifier: Annotated[MergedDistributionIdentifier, Field(frozen=True)]
