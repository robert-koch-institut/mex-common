from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import (
    AccessPlatformID,
    AccessRestriction,
    DistributionID,
    Link,
    PersonID,
    Timestamp,
    VocabularyEnum,
)


class MIMEType(VocabularyEnum):
    """The mime type."""

    __vocabulary__ = "mime-type"


class BaseDistribution(BaseModel):
    """A specific representation of a dataset."""

    stableTargetId: DistributionID
    accessService: AccessPlatformID | None = None
    accessRestriction: AccessRestriction = Field(
        ...,
        examples=["https://mex.rki.de/item/access-restriction-1"],
    )
    accessURL: Link | None = None
    author: list[PersonID] = []
    contactPerson: list[PersonID] = []
    dataCurator: list[PersonID] = []
    dataManager: list[PersonID] = []
    downloadURL: Link | None = None
    issued: Timestamp
    license: list[Link] = []
    mediaType: MIMEType | None = Field(
        None,
        examples=["https://mex.rki.de/item/mime-type-1"],
    )
    modified: list[Timestamp] = []
    otherContributor: list[PersonID] = []
    projectLeader: list[PersonID] = []
    projectManager: list[PersonID] = []
    publisher: list[PersonID] = Field(..., min_length=1)
    researcher: list[PersonID] = []
    title: str = Field(
        ...,
        examples=["theNameOfTheFile"],
        min_length=1,
    )


class ExtractedDistribution(BaseDistribution, ExtractedData):
    """An automatically extracted metadata set describing a distribution."""


class MergedDistribution(BaseDistribution, MergedItem):
    """The result of merging all extracted data and rules for a distribution."""
