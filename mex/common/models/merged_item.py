from typing import TYPE_CHECKING
from mex.common.models.entity import BaseEntity
from mex.common.types.identifier import Identifier


class MergedItem(BaseEntity):
    """Base model for all merged item classes."""
    if TYPE_CHECKING:
        identifier: Identifier
