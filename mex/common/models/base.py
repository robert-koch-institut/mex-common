import hashlib
import pickle  # nosec
from abc import abstractmethod
from collections import ChainMap
from enum import Enum
from functools import cache
from typing import TYPE_CHECKING, Any, Optional, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, model_validator

# from pydantic.fields import ModelField
ModelField = object

from mex.common.types import Identifier

ModelValuesT = TypeVar("ModelValuesT", bound=dict[str, Any])
UNSET = object()


class FlatValueMap(ChainMap[str, Any]):
    """View to mappings that flattens lists, enums and replaces Nones with `N/A`."""

    def __getitem__(self, key: str) -> str:
        """Look up `key` in the underlying mappings and return a string representation.

        Args:
            key: Mapping key to look up

        Returns:
            str: Joined list, enum value, stringified value, or default `N/A`
        """

        def transform(value: Any) -> str:
            if value is None:
                return "N/A"
            if isinstance(value, (list, tuple, set)):
                return ", ".join(transform(v) for v in value)
            if isinstance(value, Enum):
                return str(value.value)
            return str(value)

        try:
            value = super().__getitem__(key)
        except:
            value = None
        return transform(value)


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
        return {
            field.alias or field.name: field.name for field in cls.__fields__.values()
        }

    @classmethod
    @cache
    def _get_list_field_names(cls) -> list[str]:
        """Build a cached list of fields that look like lists."""
        list_fields = []
        for field in cls.__fields__.values():
            try:
                if issubclass(field.outer_type_.__origin__, list):
                    list_fields.append(field.name)
            except (TypeError, AttributeError):
                continue
        return list_fields

    @classmethod
    def _convert_non_list_to_list(
        cls, field: ModelField, value: Any
    ) -> Optional[list[Any]]:
        """Convert a non-list value to a list value by wrapping it in a list."""
        if value is None:
            if field.allow_none:
                # if the field is allowed to be None, we can leave it at None
                return None
            # if a list is required, we interpret None as an empty list
            return []
        # if the value is non-None, wrap it in a list
        return [value]

    @classmethod
    def _convert_list_to_non_list(cls, field: ModelField, value: list[Any]) -> Any:
        """Convert a list value to a non-list value by unpacking it if possible."""
        length = len(value)
        if length == 0:
            # the field might still be required, but that is validated later
            return None
        if length == 1:
            # if we have just one entry, we can safely unpack it
            return value[0]
        # we cannot unambiguously unpack more than one value
        raise ValueError(f"got multiple values for {field.name}")

    @classmethod
    def _fix_value_listyness_for_field(cls, field: ModelField, value: Any) -> Any:
        """Check actual and desired shape of a value and fix it if necesary."""
        should_be_list = field.name in cls._get_list_field_names()
        is_list = isinstance(value, list)
        if not is_list and should_be_list:
            return cls._convert_non_list_to_list(field, value)
        if is_list and not should_be_list:
            return cls._convert_list_to_non_list(field, value)
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
            if field := cls.__fields__.get(field_name):
                values[name] = cls._fix_value_listyness_for_field(field, value)
        return values

    def checksum(self) -> str:
        """Calculate md5 checksum for this model."""
        return hashlib.md5(pickle.dumps(self)).hexdigest()  # nosec

    def __str__(self) -> str:
        """Format this model as a string for logging."""
        return f"{self.__class__.__name__}: {self.checksum()}"


class MExModel(BaseModel):
    """Abstract base model for extracted data and MEx entity classes."""

    model_config = ConfigDict(extra="forbid")

    if TYPE_CHECKING:
        stableTargetId: Any

    identifier: Identifier = Field(
        ...,
        description="The identifier of this instance.",
        examples=[Identifier.generate(seed=42)],
    )

    @classmethod
    @abstractmethod
    def get_entity_type(cls) -> str:
        """Get the schema-conform name of this model class."""
        ...
