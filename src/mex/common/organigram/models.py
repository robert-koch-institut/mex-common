from mex.common.models import BaseModel
from mex.common.types import Link, Text


class OrganigramUnit(BaseModel):
    """Organizational units in the format of the organigram JSON file."""

    shortName: list[Text]
    email: list[str] = []
    identifier: str
    name: list[Text]
    alternativeName: list[Text] = []
    parentUnit: None | str = None
    website: None | Link = None
