import hashlib
import pickle
from collections.abc import MutableMapping
from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ValidatorFunctionWrapHandler, model_validator
from pydantic.json_schema import DEFAULT_REF_TEMPLATE, JsonSchemaMode
from pydantic.json_schema import GenerateJsonSchema as PydanticJsonSchemaGenerator

from mex.common.models.base.schema import JsonSchemaGenerator
from mex.common.utils import (
    get_alias_lookup,
    get_all_fields,
    get_field_names_allowing_none,
    get_list_field_names,
)


class BaseModel(
    PydanticBaseModel,
    str_strip_whitespace=True,
    populate_by_name=True,
    extra="ignore",
    str_max_length=10**5,
    str_min_length=1,
    use_enum_values=True,
    validate_default=True,
    validate_assignment=True,
):
    """Common base class for all MEx model classes."""

    @classmethod
    def model_json_schema(
        cls,
        by_alias: bool = True,  # noqa: FBT001, FBT002
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
    def _convert_non_list_to_list(cls, field_name: str, value: Any) -> list[Any] | None:  # noqa: ANN401
        """Convert a non-list value to a list value by wrapping it in a list."""
        if value is None:
            if field_name in get_field_names_allowing_none(cls):
                return None
            # if a list is required, we interpret None as an empty list
            return []
        # if the value is non-None, wrap it in a list
        return [value]

    @classmethod
    def _convert_list_to_non_list(cls, field_name: str, value: list[Any]) -> Any:  # noqa: ANN401
        """Convert a list value to a non-list value by unpacking it if possible."""
        length = len(value)
        if length == 0:
            # the field might still be required, but that is validated later
            return None
        if length == 1:
            # if we have just one entry, we can safely unpack it
            return value[0]
        # we cannot unambiguously unpack more than one value
        msg = f"got multiple values for {field_name}"
        raise ValueError(msg)

    @classmethod
    def _fix_value_listyness_for_field(cls, field_name: str, value: Any) -> Any:  # noqa: ANN401
        """Check actual and desired shape of a value and fix it if necessary."""
        should_be_list = field_name in get_list_field_names(cls)
        is_list = isinstance(value, list)
        if not is_list and should_be_list:
            return cls._convert_non_list_to_list(field_name, value)
        if is_list and not should_be_list:
            return cls._convert_list_to_non_list(field_name, value)
        # already desired shape
        return value

    @model_validator(mode="wrap")
    @classmethod
    def verify_computed_field_consistency(
        cls,
        data: Any,  # noqa: ANN401
        handler: ValidatorFunctionWrapHandler,
    ) -> Any:  # noqa: ANN401
        """Validate that parsed values for computed fields are consistent.

        Parsing a dictionary with a value for a computed field that is consistent with
        what that field would have computed anyway is allowed. Omitting values for
        computed fields is perfectly valid as well. However, if the parsed value is
        different from the computed value, a validation error is raised.

        Args:
            data: Raw data or instance to be parsed
            handler: Validator function wrap handler

        Returns:
            data with consistent computed fields.
        """
        if not cls.model_computed_fields:
            # no computed fields: exit early
            return handler(data)
        if isinstance(data, cls):
            # data is a model instance: we can assume no computed field was set,
            # because pydantic would throw an AttributeError if you tried
            return handler(data)
        if not isinstance(data, MutableMapping):
            # data is not a dictionary: we can't "pop" values from that,
            # so we can't safely do a before/after comparison
            msg = (
                "Input should be a valid dictionary, validating other types is not "
                "supported for models with computed fields."
            )
            raise AssertionError(msg)  # noqa: TRY004
        custom_values = {
            field: value
            for field in cls.model_computed_fields
            if (value := data.pop(field, None))
        }
        result = handler(data)
        computed_values = result.model_dump(include=set(custom_values))
        if computed_values != custom_values:
            msg = "Cannot set computed fields to custom values!"
            raise ValueError(msg)
        return result

    @model_validator(mode="wrap")
    @classmethod
    def fix_listyness(cls, data: Any, handler: ValidatorFunctionWrapHandler) -> Any:  # noqa: ANN401
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
            data: Raw data or instance to be parsed
            handler: Validator function wrap handler

        Returns:
            data with fixed list shapes
        """
        # TODO(ND): This needs to be a "wrap" validator that is defined *after* the
        # computed field model validator, so it runs *before* the computed field
        # validator. Sigh, see https://github.com/pydantic/pydantic/discussions/7434
        if isinstance(data, MutableMapping):
            for name, value in data.items():
                field_name = get_alias_lookup(cls).get(name, name)
                if field_name in get_all_fields(cls):
                    data[name] = cls._fix_value_listyness_for_field(field_name, value)
        return handler(data)

    def __str__(self) -> str:
        """Format this model as a string with its hash for identification."""
        return f"{self.__class__.__name__}(hash='{hex(hash(self))}')"

    def __hash__(self) -> int:
        """Calculate a hash to make the model usable in sets, dicts and caches.

        Creates a blake2b hash of the model by serializing it with pickle
        and computing a hash digest.

        Returns:
            Hash representing the model's current state.
        """
        serialized = pickle.dumps(self, protocol=pickle.HIGHEST_PROTOCOL)
        digest = hashlib.blake2b(serialized, usedforsecurity=False)
        return int(digest.hexdigest(), 16)
