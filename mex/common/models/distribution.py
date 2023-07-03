from pydantic import Field

from mex.common.models.extracted_data import ExtractedData
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
    """the mime type."""

    __vocabulary__ = "mime-type"


class ExtractedDistribution(ExtractedData):
    """A distribution."""

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
    publisher: list[PersonID] = Field(..., min_items=1)
    researcher: list[PersonID] = []
    title: str = Field(
        ...,
        examples=["theNameOfTheFile"],
        min_length=1,
    )
