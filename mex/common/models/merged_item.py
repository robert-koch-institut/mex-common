from typing import TYPE_CHECKING

from mex.common.models.base import MExModel
from mex.common.types import Identifier


class MergedItem(MExModel):
    """Base model class definition for all merged items."""

    if TYPE_CHECKING:
        stableTargetId: Identifier

    @classmethod
    def get_entity_type(cls) -> str:
        """Get the entity-type for this model class."""
        return cls.__name__

    def __str__(self) -> str:
        """Format this merged item instance as a string for logging."""
        return f"{self.__class__.__name__}: {self.identifier}"
