from typing import TYPE_CHECKING, ClassVar

from mex.common.models.base import BaseModel
from mex.common.types import Identifier


class BaseEntity(BaseModel, extra="forbid"):
    """Abstract base model for extracted data, merged item and rule set classes.

    This class gives type hints for an `identifier` field, the frozen `entityType` field
    and the frozen class variable `stemType`.
    Subclasses should implement all three fields while setting the correct identifier
    type as well as the correct literal values for the entity and stem types.
    """

    if TYPE_CHECKING:  # pragma: no cover
        # The frozen `entityType` field is added to all `BaseEntity` subclasses to
        # help with assigning the correct class when reading raw JSON entities.
        # E.g.: https://docs.pydantic.dev/latest/concepts/fields/#discriminator
        # Simple duck-typing would not work, because some entity-types have overlapping
        # attributes, like `Person.email` and `ContactPoint.email`.
        entityType: str

        # The frozen `stemType` class variable is added to all `BaseEntity` subclasses
        # to help with knowing which special-use-case classes are meant for the same
        # type of items. E.g. `ExtractedPerson`, `MergedPerson` and `PreventivePerson`
        # all share the same `stemType` of `Person`.
        stemType: ClassVar

        # A globally unique identifier is added to all `BaseEntity` subclasses and
        # should be typed to the correct identifier type. Regardless of the entity-type
        # or whether this item was extracted, merged, etc., identifiers will be assigned
        # just once and should be declared as `frozen` on subclasses.


    def __str__(self) -> str:
        """Format this instance as a string for logging."""
        return f"{self.entityType}: {self.identifier}"
