from pydantic import Field

from mex.common.models.extracted_data import ExtractedData
from mex.common.types import (
    ActivityID,
    ContactPointID,
    Identifier,
    Link,
    OrganizationalUnitID,
    OrganizationID,
    PersonID,
    Text,
    Theme,
    Timestamp,
    VocabularyEnum,
)


class ActivityType(VocabularyEnum):
    """The activity type."""

    __vocabulary__ = "activity-type"


class ExtractedActivity(ExtractedData):
    """The context a resource was generated in.

    This may be a project, an area of work or an administrative procedure.
    """

    stableTargetId: ActivityID
    abstract: list[Text] = []
    activityType: list[ActivityType] = Field(
        [], examples=["https://mex.rki.de/concept/activity-type-1"]
    )
    alternativeTitle: list[Text] = []
    contact: list[OrganizationalUnitID | PersonID | ContactPointID] = Field(
        ...,
        examples=[Identifier.generate(seed=42)],
        min_items=1,
    )
    documentation: list[Link] = []
    end: list[Timestamp] = Field(
        [],
        examples=["2024-01-17", "2024", "2024-01"],
    )
    externalAssociate: list[OrganizationalUnitID | PersonID] = []
    funderOrCommissioner: list[OrganizationID] = []
    fundingProgram: list[str] = []
    involvedPerson: list[PersonID] = []
    involvedUnit: list[OrganizationalUnitID] = []
    isPartOfActivity: list[ActivityID] = []
    publication: list[Link] = []
    responsibleUnit: list[OrganizationalUnitID] = Field(
        ...,
        min_items=1,
    )
    shortName: list[Text] = []
    start: list[Timestamp] = Field(
        [],
        examples=["2023-01-16", "2023", "2023-02"],
    )
    succeeds: list[ActivityID] = []
    theme: list[Theme] = Field([], examples=["https://mex.rki.de/concept/theme-1"])
    title: list[Text] = Field(..., min_items=1)
    website: list[Link] = []
