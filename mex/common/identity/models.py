from mex.common.models import BaseModel
from mex.common.types import Identifier, PrimarySourceID


class Identity(BaseModel):
    """Model for identifier lookup."""

    identifier: Identifier
    hadPrimarySource: PrimarySourceID
    identifierInPrimarySource: str
    stableTargetId: Identifier
