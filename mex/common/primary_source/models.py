from mex.common.models import BaseModel
from mex.common.types import Text


class SeedPrimarySource(BaseModel):
    """Model class for primary sources coming from the raw-data JSON file."""

    identifier: str
    title: list[Text] = []
