from typing import TYPE_CHECKING, ClassVar

from pydantic import ConfigDict

from mex.common.models.base.model import BaseModel


class BaseEntity(BaseModel):
    """Base model for extracted item, preview item, merged item, rule-related classes.

    This class gives type hints for the frozen `entityType` field and the frozen class
    variable `stemType`.
    Subclasses should implement both fields and set the correct literal values.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

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
