from pydantic import AnyUrl

from mex.common.models.base import BaseModel


class OrganigramName(BaseModel):
    """Organigram unit name translated in German and English."""

    de: str
    en: str


class OrganigramWebsite(BaseModel):
    """Organigram unit website."""

    language: str
    title: str
    url: AnyUrl


class OrganigramUnit(BaseModel):
    """Organizational units in the format of the organigram JSON file."""

    shortName: str
    email: list[str] = []
    identifier: str
    name: OrganigramName
    alternativeName: list[str] = []
    parentUnit: None | str
    website: None | OrganigramWebsite
