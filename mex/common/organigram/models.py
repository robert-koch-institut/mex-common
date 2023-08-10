from mex.common.models import BaseModel
from mex.common.types import Link


class OrganigramName(BaseModel):
    """Organigram unit name translated in German and English."""

    de: str
    en: str


class OrganigramUnit(BaseModel):
    """Organizational units in the format of the organigram JSON file."""

    shortName: str
    email: list[str] = []
    identifier: str
    name: OrganigramName
    alternativeName: list[str] = []
    parentUnit: None | str
    website: None | Link
