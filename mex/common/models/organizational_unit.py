from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import Email, Link, OrganizationalUnitID, OrganizationID, Text


class BaseOrganizationalUnit(BaseModel):
    """An organizational unit which is part of some larger organization."""

    alternativeName: list[Text] = []
    email: list[Email] = []
    name: Annotated[list[Text], Field(min_length=1)]
    parentUnit: OrganizationalUnitID | None = None
    shortName: list[Text] = []
    unitOf: list[OrganizationID] = []
    website: list[Link] = []


class ExtractedOrganizationalUnit(BaseOrganizationalUnit, ExtractedData):
    """An automatically extracted metadata set describing an organizational unit."""

    entityType: Literal["ExtractedOrganizationalUnit"] = Field(
        "ExtractedOrganizationalUnit", alias="$type", frozen=True
    )
    stableTargetId: OrganizationalUnitID


class MergedOrganizationalUnit(BaseOrganizationalUnit, MergedItem):
    """The result of merging all extracted data and rules for an organizational unit."""

    entityType: Literal["MergedOrganizationalUnit"] = Field(
        "MergedOrganizationalUnit", alias="$type", frozen=True
    )
