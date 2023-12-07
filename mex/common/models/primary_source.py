from pydantic import Field

from mex.common.models.base import MExModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import (
    ContactPointID,
    Link,
    OrganizationalUnitID,
    PersonID,
    PrimarySourceID,
    Text,
)


class BasePrimarySource(MExModel):
    """A collection of information, that is managed and curated by an RKI unit."""

    stableTargetId: PrimarySourceID
    alternativeTitle: list[Text] = []
    contact: list[OrganizationalUnitID | PersonID | ContactPointID] = []
    description: list[Text] = []
    documentation: list[Link] = []
    locatedAt: list[Link] = []
    title: list[Text] = []
    unitInCharge: list[OrganizationalUnitID] = []
    version: str | None = Field(
        None,
        examples=["v1", "2023-01-16", "Schema 9"],
    )


class ExtractedPrimarySource(BasePrimarySource, ExtractedData):
    """An automatically extracted metadata set describing a primary source."""


class MergedPrimarySource(BasePrimarySource, MergedItem):
    """The result of merging all extracted data and rules for a primary source."""
