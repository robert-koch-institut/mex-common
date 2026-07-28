from typing import TYPE_CHECKING

from pydantic.json_schema import (
    GenerateJsonSchema as PydanticJsonSchemaGenerator,
)
from pydantic.json_schema import JsonSchemaValue

if TYPE_CHECKING:
    from pydantic._internal._core_utils import CoreSchemaOrField


class JsonSchemaGenerator(PydanticJsonSchemaGenerator):
    """Customization of the pydantic class for generating JSON schemas."""

    def field_title_should_be_set(self, schema: "CoreSchemaOrField") -> bool:  # noqa: ARG002
        """Disable pydantic behavior to derive field titles from field names.

        For example, pydantic would add
            {"title": "Had Primary Source"}
        to the schema of the `hadPrimarySource` field, but mex-model does not
        specify titles for fields, so we omit them entirely.
        Titles that the annotated types set themselves (e.g. identifiers and
        vocabularies) are not affected by this, because pydantic only derives
        a title when the field schema does not have one yet.
        """
        return False

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
