from typing import Generic, TypeVar

from mex.common.models.entity import BaseEntity
from mex.common.types.identifier import MergedIdentifier

MergedIdentifierT = TypeVar("MergedIdentifierT", bound=MergedIdentifier)


class MergedItem(Generic[MergedIdentifierT], BaseEntity):
    """Base model for all merged item classes."""

    identifier: MergedIdentifier
