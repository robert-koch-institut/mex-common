from typing import Annotated, Generic, TypeVar

from pydantic import Field

from mex.common.models import BaseModel
from mex.common.types import (
    ExtractedIdentifier,
    MergedIdentifier,
    MergedPrimarySourceIdentifier,
)

ExtractedIdentifierT = TypeVar("ExtractedIdentifierT", bound=ExtractedIdentifier)
MergedIdentifierT = TypeVar("MergedIdentifierT", bound=MergedIdentifier)


class Identity(Generic[ExtractedIdentifierT, MergedIdentifierT], BaseModel):
    """Model for identifier lookup."""

    identifier: Annotated[ExtractedIdentifierT, Field(frozen=True)]
    hadPrimarySource: Annotated[MergedPrimarySourceIdentifier, Field(frozen=True)]
    identifierInPrimarySource: Annotated[str, Field(frozen=True)]
    stableTargetId: Annotated[MergedIdentifierT, Field(frozen=True)]
