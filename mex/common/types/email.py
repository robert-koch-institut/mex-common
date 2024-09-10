from typing import Any

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, json_schema
from pydantic_core import core_schema

EMAIL_PATTERN = r"^[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+$"


class Email(str):
    """Email address of a person, organization or other entity."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Modify the core schema to add the email regex."""
        return core_schema.str_schema(pattern=EMAIL_PATTERN)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema_: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> json_schema.JsonSchemaValue:
        """Modify the json schema to add a title, format and examples."""
        json_schema_ = handler(core_schema_)
        json_schema_["title"] = cls.__name__
        json_schema_["format"] = "email"
        json_schema_["examples"] = ["info@rki.de"]
        return json_schema_
