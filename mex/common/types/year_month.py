from typing import Any, Type

from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

YEAR_MONTH_PATTERN = r"^\d{4}(-\d{2})?$"


class YearMonth(str):
    """Partial date pattern that accepts YYYY or YYYY-MM format."""

    @classmethod
    def __get_pydantic_core_schema__(cls, _source: Type[Any]) -> core_schema.CoreSchema:
        """Get pydantic core schema."""
        return core_schema.str_schema(pattern=YEAR_MONTH_PATTERN)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema_: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Add title and format."""
        field_schema = handler(core_schema_)
        field_schema = handler.resolve_ref_schema(field_schema)
        field_schema["title"] = cls.__name__
        field_schema["examples"] = ["2024", "1999-04"]
        return field_schema
