import hashlib
import pickle  # nosec
from collections.abc import MutableMapping
from functools import cache
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

from pydantic import (
    BaseModel as PydanticBaseModel,
)
from pydantic import (
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    model_validator,
)
from pydantic.fields import FieldInfo
from pydantic.json_schema import DEFAULT_REF_TEMPLATE, JsonSchemaMode, JsonSchemaValue
from pydantic.json_schema import (
    GenerateJsonSchema as PydanticJsonSchemaGenerator,
)

from mex.common.types import Identifier

RawModelDataT = TypeVar("RawModelDataT")


class JsonSchemaGenerator(PydanticJsonSchemaGenerator):
    """Customization of the pydantic class for generating JSON schemas."""

    def handle_ref_overrides(self, json_schema: JsonSchemaValue) -> JsonSchemaValue:
        """Disable pydantic behavior to wrap top-level `$ref` keys in an `allOf`.

        For example, pydantic would convert
            {"$ref": "#/$defs/APIType", "examples": ["api-type-1"]}
        into
            {"allOf": {"$ref": "#/$defs/APIType"}, "examples": ["api-type-1"]}
        which is in fact recommended by JSON schema, but we need to disable this
        to stay compatible with mex-editor and mex-model.
        """
        return json_schema


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
    def _get_field_names_allowing_none(cls) -> list[str]:
        """Build a cached list of fields can be set to None."""
        fields: list[str] = []
        for name, field_info in cls.model_fields.items():
            validator = TypeAdapter(field_info.annotation)
            try:
                validator.validate_python(None)
            except ValidationError:
                continue
            fields.append(name)
        return fields

    @classmethod
    def _convert_non_list_to_list(
        cls, name: str, field: FieldInfo, value: Any
    ) -> list[Any] | None:
        """Convert a non-list value to a list value by wrapping it in a list."""
        if value is None:
            if name in cls._get_field_names_allowing_none():
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
            return cls._convert_non_list_to_list(name, field, value)
        if is_list and not should_be_list:
            return cls._convert_list_to_non_list(name, value)
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
                if field := cls.model_fields.get(field_name):
                    data[name] = cls._fix_value_listyness_for_field(
                        field_name, field, value
                    )
        return data

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

    identifier: Annotated[
        Identifier,
        Field(
            description=(
                "A globally unique identifier for this item. Regardless of the "
                "entity-type or whether this item was extracted, merged, etc. "
                "identifiers will be assigned just once."
            ),
        ),
    ]
