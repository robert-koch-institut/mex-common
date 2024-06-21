import hashlib
import json
from collections.abc import MutableMapping
from functools import cache
from types import UnionType
from typing import (
    Any,
    TypeVar,
    Union,
)

from pydantic import BaseModel as PydanticBaseModel
from pydantic import (
    ConfigDict,
    TypeAdapter,
    ValidationError,
    model_validator,
)
from pydantic.json_schema import DEFAULT_REF_TEMPLATE, JsonSchemaMode
from pydantic.json_schema import GenerateJsonSchema as PydanticJsonSchemaGenerator

from mex.common.models.schema import JsonSchemaGenerator
from mex.common.transform import MExEncoder
from mex.common.utils import get_inner_types

RawModelDataT = TypeVar("RawModelDataT")


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
    def model_json_schema(
        cls,
        by_alias: bool = True,
        ref_template: str = DEFAULT_REF_TEMPLATE,
        schema_generator: type[PydanticJsonSchemaGenerator] = JsonSchemaGenerator,
        mode: JsonSchemaMode = "validation",
    ) -> dict[str, Any]:
        """Generates a JSON schema for a model class.

        Args:
            by_alias: Whether to use attribute aliases or not.
            ref_template: The reference template.
            schema_generator: Overriding the logic used to generate the JSON schema
            mode: The mode in which to generate the schema.

        Returns:
            The JSON schema for the given model class.
        """
        return super().model_json_schema(
            by_alias=by_alias,
            ref_template=ref_template,
            schema_generator=schema_generator,
            mode=mode,
        )

    @classmethod
    @cache
    def _get_alias_lookup(cls) -> dict[str, str]:
        """Build a cached mapping from field alias to field names."""
        return {
            field_info.alias or field_name: field_name
            for field_name, field_info in cls.model_fields.items()
        }

    @classmethod
    @cache
    def _get_list_field_names(cls) -> list[str]:
        """Build a cached list of fields that look like lists."""
        field_names = []
        for field_name, field_info in cls.model_fields.items():
            field_types = get_inner_types(
                field_info.annotation, unpack=(Union, UnionType)
            )
            if any(
                isinstance(field_type, type) and issubclass(field_type, list)
                for field_type in field_types
            ):
                field_names.append(field_name)
        return field_names

    @classmethod
    @cache
    def _get_field_names_allowing_none(cls) -> list[str]:
        """Build a cached list of fields can be set to None."""
        field_names: list[str] = []
        for field_name, field_info in cls.model_fields.items():
            validator = TypeAdapter(field_info.annotation)
            try:
                validator.validate_python(None)
            except ValidationError:
                continue
            field_names.append(field_name)
        return field_names

    @classmethod
    def _convert_non_list_to_list(cls, field_name: str, value: Any) -> list[Any] | None:
        """Convert a non-list value to a list value by wrapping it in a list."""
        if value is None:
            if field_name in cls._get_field_names_allowing_none():
                return None
            # if a list is required, we interpret None as an empty list
            return []
        # if the value is non-None, wrap it in a list
        return [value]

    @classmethod
    def _convert_list_to_non_list(cls, field_name: str, value: list[Any]) -> Any:
        """Convert a list value to a non-list value by unpacking it if possible."""
        length = len(value)
        if length == 0:
            # the field might still be required, but that is validated later
            return None
        if length == 1:
            # if we have just one entry, we can safely unpack it
            return value[0]
        # we cannot unambiguously unpack more than one value
        raise ValueError(f"got multiple values for {field_name}")

    @classmethod
    def _fix_value_listyness_for_field(cls, field_name: str, value: Any) -> Any:
        """Check actual and desired shape of a value and fix it if necessary."""
        should_be_list = field_name in cls._get_list_field_names()
        is_list = isinstance(value, list)
        if not is_list and should_be_list:
            return cls._convert_non_list_to_list(field_name, value)
        if is_list and not should_be_list:
            return cls._convert_list_to_non_list(field_name, value)
        # already desired shape
        return value

    @model_validator(mode="before")
    @classmethod
    def fix_listyness(cls, data: RawModelDataT) -> RawModelDataT:
        """Adjust the listyness of to-be-parsed data to match the desired shape.

        If that data is a Mapping and the model defines a list[T] field but the raw data
        contains just a value of type T, it will be wrapped into a list. If the raw
        data contains a literal `None`, but the list field is defined as required, we
        substitute an empty list.

        If the model does not expect a list, but the raw data contains a list with
        no entries, it will be substituted with `None`. If the raw data contains exactly
        one entry, then it will be unpacked from the list. If it contains more than one
        entry however, an error is raised, because we would not know which to choose.

        Args:
            data: Raw data to be parsed

        Returns:
            data with fixed list shapes
        """
        if isinstance(data, MutableMapping):
            for name, value in data.items():
                field_name = cls._get_alias_lookup().get(name, name)
                if field_name in cls.model_fields:
                    data[name] = cls._fix_value_listyness_for_field(field_name, value)
        return data

    def checksum(self) -> str:
        """Calculate md5 checksum for this model."""
        json_str = json.dumps(self, sort_keys=True, cls=MExEncoder)
        return hashlib.md5(json_str.encode()).hexdigest()  # noqa: S324

    def __str__(self) -> str:
        """Format this model as a string for logging."""
        return f"{self.__class__.__name__}: {self.checksum()}"
