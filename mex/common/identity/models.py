from typing import Annotated

from pydantic import Field

from mex.common.models import BaseModel
from mex.common.types import Identifier, PrimarySourceID


class Identity(BaseModel):
    """Model for identifier lookup."""

    identifier: Annotated[Identifier, Field(frozen=True)]
    hadPrimarySource: Annotated[PrimarySourceID, Field(frozen=True)]
    identifierInPrimarySource: Annotated[str, Field(frozen=True)]
    stableTargetId: Annotated[Identifier, Field(frozen=True)]
