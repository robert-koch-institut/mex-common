import hashlib
import pickle  # nosec
from abc import abstractmethod
from functools import cache
from typing import TYPE_CHECKING, Any, Optional, TypeVar, Union, get_args, get_origin

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, TypeAdapter, ValidationError, model_validator
from pydantic.fields import FieldInfo

from mex.common.types import Identifier

ModelValuesT = TypeVar("ModelValuesT", bound=dict[str, Any])


class BaseModel(PydanticBaseModel):
    """Common base class for all MEx model classes."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        populate_by_name=True,
        extra="ignore",
        str_max_length=10**5,
        str_min_length=1,
        use_enum_values=True,
        validate_default=True,
        validate_assignment=True,
    )

    @classmethod
    @cache
    def _get_alias_lookup(cls) -> dict[str, str]:
        """Build a cached mapping from field alias to field names."""
        return {field.alias or name: name for name, field in cls.model_fields.items()}

    @classmethod
    @cache
    def _get_list_field_names(cls) -> list[str]:
        """Build a cached list of fields that look like lists."""

        def is_object_subclass_of_list(obj: Any) -> bool:
            try:
                return issubclass(obj, list)
            except TypeError:
                return False

        list_fields = []
        for name, field in cls.model_fields.items():
            origin = get_origin(field.annotation)
            if is_object_subclass_of_list(origin):
                list_fields.append(name)
            elif origin is Union:
                for arg in get_args(field.annotation):
                    if is_object_subclass_of_list(get_origin(arg)):
                        list_fields.append(name)
                        break
        return list_fields

    @classmethod
    @cache
    def _is_none_allowed(cls, annotation: type | None) -> bool:
        """Check if None is an allowed value for the provided annotation.

        caches results
        """
        validator = TypeAdapter(annotation)
        try:
            validator.validate_python(None)
        except ValidationError:
            return False
        return True

    @classmethod
    def _convert_non_list_to_list(
        cls, field: FieldInfo, value: Any
    ) -> Optional[list[Any]]:
        """Convert a non-list value to a list value by wrapping it in a list."""
        if value is None:
            if cls._is_none_allowed(field.annotation):
                return None
            # if a list is required, we interpret None as an empty list
            return []
        # if the value is non-None, wrap it in a list
        return [value]

    @classmethod
    def _convert_list_to_non_list(cls, name: str, value: list[Any]) -> Any:
        """Convert a list value to a non-list value by unpacking it if possible."""
        length = len(value)
        if length == 0:
            # the field might still be required, but that is validated later
            return None
        if length == 1:
            # if we have just one entry, we can safely unpack it
            return value[0]
        # we cannot unambiguously unpack more than one value
        raise ValueError(f"got multiple values for {name}")

    @classmethod
    def _fix_value_listyness_for_field(
        cls, name: str, field: FieldInfo, value: Any
    ) -> Any:
        """Check actual and desired shape of a value and fix it if necessary."""
        should_be_list = name in cls._get_list_field_names()
        is_list = isinstance(value, list)
        if not is_list and should_be_list:
            return cls._convert_non_list_to_list(field, value)
        if is_list and not should_be_list:
            return cls._convert_list_to_non_list(name, value)
        # already desired shape
        return value

    @model_validator(mode="before")
    @classmethod
    def fix_listyness(cls, values: ModelValuesT) -> ModelValuesT:
        """Adjust the listyness of to-be-parsed values to match the desired shape.

        If the model defines a list[T] field but the raw data contains just a value
        of type T, it will be wrapped into a list. If the raw data contains a literal
        `None`, but the list field is defined as required, we substitute an empty list.

        If the model does not expect a list, but the raw data contains a list with
        no entries, it will be substituted with `None`. If the raw data contains exactly
        one entry, then it will be unpacked from the list. If it contains more than one
        entry however, an error is raised, because we would not know which to choose.

        Args:
            values: Raw values to be parsed

        Returns:
            dict: Values with fixed list shapes
        """
        for name, value in values.items():
            field_name = cls._get_alias_lookup().get(name, name)
            if field := cls.model_fields.get(field_name):
                values[name] = cls._fix_value_listyness_for_field(
                    field_name, field, value
                )
        return values

    def checksum(self) -> str:
        """Calculate md5 checksum for this model."""
        return hashlib.md5(pickle.dumps(self)).hexdigest()  # noqa: S324

    def __str__(self) -> str:
        """Format this model as a string for logging."""
        return f"{self.__class__.__name__}: {self.checksum()}"


class MExModel(BaseModel):
    """Abstract base model for extracted data and merged item classes.

    This class only defines an `identifier` and gives a type hint for `stableTargetId`.
    """

    model_config = ConfigDict(extra="forbid")

    if TYPE_CHECKING:
        # Sometimes multiple primary sources describe the same activity, resource, etc.
        # and a complete metadata item can only be created by merging these fragments.
        # The `stableTargetID` is part of all models in `mex.common.models` to allow
        # MEx to identify which extracted items describe the same thing and should be
        # merged to create a complete metadata item.
        # The name might be a bit misleading (also due to historical reasons), but the
        # "stability" is only guaranteed for one "real world" or "digital world" thing
        # having the same ID in MEx over time. But not as a guarantee, that the same
        # metadata sources contribute to the complete metadata item.
        # Because we anticipate that items have to be merged, the `stableTargetID` is
        # also used as the foreign key for all fields containing references.
        stableTargetId: Any

    identifier: Identifier = Field(
        ...,
        description=(
            "A globally unique identifier for this item. Regardless of the entity-type "
            "or whether this item was extracted, merged, etc. identifiers will be "
            "assigned just once."
        ),
        examples=[Identifier.generate(seed=42)],
    )

    @classmethod
    @abstractmethod
    def get_entity_type(cls) -> str:
        """Get the schema-conform name of this model class."""
        ...
