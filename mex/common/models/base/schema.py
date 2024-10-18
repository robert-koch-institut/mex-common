from pydantic.json_schema import (
    GenerateJsonSchema as PydanticJsonSchemaGenerator,
)
from pydantic.json_schema import JsonSchemaValue


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
