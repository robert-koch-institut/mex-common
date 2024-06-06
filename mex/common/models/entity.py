from typing import TYPE_CHECKING

from mex.common.models.base import BaseModel
from mex.common.types import Identifier


class BaseEntity(BaseModel, extra="forbid"):
    """Abstract base model for extracted data, merged item and rule set classes.

    This class gives type hints for an `identifier` field and the frozen class variable
    `entityType`. Subclasses should implement both fields and set the correct identifier
    type as well as the correct literal value for the entity type.
    """

    if TYPE_CHECKING:  # pragma: no cover
        # The `entityType` class variable is added to all `BaseEntity` subclasses to
        # help with assigning the correct class when reading raw JSON entities.
        # E.g.: https://docs.pydantic.dev/latest/concepts/fields/#discriminator
        # Simple duck-typing would not work, because some entity-types have overlapping
        # attributes, like `Person.email` and `ContactPoint.email`.
        entityType: str

        # A globally unique identifier is added to all `BaseEntity` subclasses and
        # should be typed to the correct identifier type. Regardless of the entity-type
        # or whether this item was extracted, merged, etc., identifiers will be assigned
        # just once and should be declared as `frozen` on subclasses.


    def __str__(self) -> str:
        """Format this instance as a string for logging."""
        return f"{self.entityType}: {self.identifier}"
