from typing import Annotated, Literal

from pydantic import Field

from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.models.merged_item import MergedItem
from mex.common.types import (
    Email,
    ExtractedOrganizationalUnitIdentifier,
    Link,
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    Text,
)


class BaseOrganizationalUnit(BaseModel):
    """An organizational unit which is part of some larger organization."""

    alternativeName: list[Text] = []
    email: list[Email] = []
    name: Annotated[list[Text], Field(min_length=1)]
    parentUnit: MergedOrganizationalUnitIdentifier | None = None
    shortName: list[Text] = []
    unitOf: list[MergedOrganizationIdentifier] = []
    website: list[Link] = []


class ExtractedOrganizationalUnit(BaseOrganizationalUnit, ExtractedData):
    """An automatically extracted metadata set describing an organizational unit."""

    entityType: Annotated[
        Literal["ExtractedOrganizationalUnit"], Field(alias="$type", frozen=True)
    ] = "ExtractedOrganizationalUnit"
    identifier: Annotated[ExtractedOrganizationalUnitIdentifier, Field(frozen=True)]
    stableTargetId: MergedOrganizationalUnitIdentifier


class MergedOrganizationalUnit(BaseOrganizationalUnit, MergedItem):
    """The result of merging all extracted data and rules for an organizational unit."""

    entityType: Annotated[
        Literal["MergedOrganizationalUnit"], Field(alias="$type", frozen=True)
    ] = "MergedOrganizationalUnit"
    identifier: Annotated[MergedOrganizationalUnitIdentifier, Field(frozen=True)]
