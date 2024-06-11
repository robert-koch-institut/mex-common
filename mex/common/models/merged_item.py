from typing import Annotated, Generic, TypeVar

from pydantic import Field

from mex.common.models.entity import BaseEntity
from mex.common.types.identifier import MergedIdentifier

MergedIdentifierT = TypeVar("MergedIdentifierT", bound=MergedIdentifier)


class MergedItem(Generic[MergedIdentifierT], BaseEntity):
    """Base model for all merged item classes."""

    identifier: Annotated[MergedIdentifierT, Field(frozen=True)]
