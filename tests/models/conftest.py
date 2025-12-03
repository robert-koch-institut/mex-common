import re
from collections.abc import Callable
from itertools import chain
from typing import Any

from mex.common.models import EXTRACTED_MODEL_CLASSES, MERGED_MODEL_CLASSES, BaseModel
from mex.common.transform import dromedary_to_kebab
from mex.common.types import IDENTIFIER_PATTERN, VOCABULARY_PATTERN
from mex.model import EXTRACTED_MODEL_JSON_BY_NAME, MERGED_MODEL_JSON_BY_NAME


def _model_to_schema(model: type[BaseModel]) -> dict[str, Any]:
    # pydantic does not include computed fields in the validation schema
    # and does not include validation rules in the serialization schema.
    # so we need to mangle those two together here, to get a schema that is
    # more comparable to what mex-model specifies.
    validation_schema = model.model_json_schema(
        ref_template="/mex/model/fields/{model}", mode="validation"
    )
    serialization_schema = model.model_json_schema(
        ref_template="/mex/model/fields/{model}", mode="serialization"
    )
    validation_schema["properties"] = {
        **serialization_schema["properties"],
        **validation_schema["properties"],
    }
    validation_schema["required"] = sorted(
        {*serialization_schema["required"], *validation_schema["required"]}
    )
    return validation_schema


GENERATED_SCHEMAS = dict(
    sorted(
        {
            schema["title"]: schema
            for schema in [
                _model_to_schema(model)
                for model in chain(EXTRACTED_MODEL_CLASSES, MERGED_MODEL_CLASSES)
            ]
        }.items()
    )
)
SPECIFIED_SCHEMAS = dict(
    sorted(
        {
            schema["title"]: schema
            for schema in chain(
                EXTRACTED_MODEL_JSON_BY_NAME.values(),
                MERGED_MODEL_JSON_BY_NAME.values(),
            )
        }.items()
    )
)
ENTITY_TYPES_AND_FIELD_NAMES_BY_FQN = {
    f"{entity_type}.{field_name}": (entity_type, field_name)
    for entity_type, schema in SPECIFIED_SCHEMAS.items()
    for field_name in schema["properties"]
}


def _sub_only_text(repl: Callable[[str], str], string: str) -> str:
    # substitute only the textual parts of a string, e.g. leave slashes alone
    return re.sub(r"([a-zA-Z_-]+)", lambda m: repl(m.group(0)), string)


def prepare_generated_field(field: str, obj: list[Any] | dict[str, Any]) -> None:
    # discard title but save value for later
    title = obj.pop("title", field)  # field title is only in generated

    # the generated schema does not use $ref for identifiers and vocabulary fields
    # so we convert the generated fields to look like the specified schema
    if obj.get("pattern") == IDENTIFIER_PATTERN:
        del obj["pattern"]
        del obj["type"]
        if field == "identifier":
            obj["$ref"] = "/mex/model/fields/identifier"
        else:
            obj["$ref"] = "/mex/model/entities/{}#/identifier".format(
                title.removesuffix("Identifier")
            )
    if obj.get("pattern") == VOCABULARY_PATTERN:
        del obj["pattern"]
        del obj["type"]
        obj["$ref"] = "/mex/model/entities/concept#/identifier"

    # make sure all refs have paths in kebab-case
    # (the models use the class names, whereas the spec uses kebab-case URLs)
    if "$ref" in obj:
        obj["$ref"] = _sub_only_text(dromedary_to_kebab, obj["$ref"])

    # recurse into the field definitions for array items
    if obj.get("type") == "array":
        prepare_generated_field(field, obj["items"])

    # recurse into choices if multiple types are allowed
    for quantifier in {"anyOf", "allOf"} & set(obj):
        for item in obj[quantifier]:
            prepare_generated_field(field, item)


def prepare_specified_field(field: str, obj: list[Any] | dict[str, Any]) -> None:
    # discard comments and descriptions
    obj.pop("$comment", None)  # only in spec

    # recurse into the field definitions for array items
    if obj.get("type") == "array":
        prepare_specified_field(field, obj["items"])

    # recurse into choices if multiple types are allowed
    for quantifier in {"anyOf", "allOf"} & set(obj):
        for item in obj[quantifier]:
            prepare_specified_field(field, item)
