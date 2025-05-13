from typing import Any

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, json_schema
from pydantic_core import core_schema

EMAIL_PATTERN = r"^[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+$"


class Email(str):
    """Email address of a person, organization or other entity."""

    __slots__ = ()

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """Modify the core schema to add the email regex."""
        return core_schema.chain_schema(
            [
                core_schema.str_schema(pattern=EMAIL_PATTERN),
                core_schema.no_info_plain_validator_function(cls),
            ],
            serialization=core_schema.to_string_ser_schema(when_used="unless-none"),
        )

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

    def __repr__(self) -> str:
        """Overwrite the default representation."""
        return f'{self.__class__.__name__}("{self}")'
