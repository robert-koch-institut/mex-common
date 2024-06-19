from typing import TYPE_CHECKING, ClassVar

from mex.common.models.base import BaseModel


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
