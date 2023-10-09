from typing import Any, Type

from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

EMAIL_PATTERN = r".+@.+"


class Email(str):
    """Email address of a person, organization or other entity."""

    @classmethod
    def __get_pydantic_core_schema__(cls, _source: Type[Any]) -> core_schema.CoreSchema:
        """Get pydanctic core schema."""
        return core_schema.str_schema(pattern=EMAIL_PATTERN)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema_: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Add title and format."""
        field_schema = handler(core_schema_)
        field_schema.update(title=cls.__name__, format="email")
        return field_schema
