import json
import re
from collections.abc import Callable
from copy import deepcopy
from itertools import zip_longest
from typing import Any

import pytest

from mex.common.models import EXTRACTED_MODEL_CLASSES, BaseModel
from mex.common.transform import dromedary_to_kebab
from mex.common.types import IDENTIFIER_PATTERN, VOCABULARY_PATTERN
from mex.model import ENTITY_JSON_BY_NAME


def model_to_schema(model: type[BaseModel]) -> dict[str, Any]:
    # pydantic does not include computed fields in the validation schema
    # and does not include validation rules in the serialization schema.
    # so we need to mangle those two together here, to get a schema that is
    # more comparable to what mex-model specifies.

    validation_schema = model.model_json_schema(
        ref_template="/schema/fields/{model}", mode="validation"
    )
    serialization_schema = model.model_json_schema(
        ref_template="/schema/fields/{model}", mode="serialization"
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
            for schema in [model_to_schema(model) for model in EXTRACTED_MODEL_CLASSES]
        }.items()
    )
)
SPECIFIED_SCHEMAS = dict(
    sorted({schema["title"]: schema for schema in ENTITY_JSON_BY_NAME.values()}.items())
)
ENTITY_TYPES_AND_FIELD_NAMES_BY_FQN = {
    f"{entity_type}.{field_name}": (entity_type, field_name)
    for entity_type, schema in SPECIFIED_SCHEMAS.items()
    for field_name in schema["properties"]
}


def test_entity_types_match_spec() -> None:
    assert list(GENERATED_SCHEMAS) == list(SPECIFIED_SCHEMAS)


@pytest.mark.parametrize(
    ("generated", "specified"),
    zip_longest(GENERATED_SCHEMAS.values(), SPECIFIED_SCHEMAS.values(), fillvalue={}),
    ids=map(str, zip_longest(GENERATED_SCHEMAS, SPECIFIED_SCHEMAS, fillvalue="N/A")),
)
def test_field_names_match_spec(
    generated: dict[str, Any], specified: dict[str, Any]
) -> None:
    ignored_field_names = {
        "$type",  # only in generated
    }
    generated_field_names = {
        k: v for k, v in generated["properties"].items() if k not in ignored_field_names
    }
    specified_field_names = set(specified["properties"])
    assert set(generated_field_names) == specified_field_names


@pytest.mark.parametrize(
    ("generated", "specified"),
    zip_longest(GENERATED_SCHEMAS.values(), SPECIFIED_SCHEMAS.values(), fillvalue={}),
    ids=map(str, zip_longest(GENERATED_SCHEMAS, SPECIFIED_SCHEMAS, fillvalue="N/A")),
)
def test_entity_type_matches_metadata(
    generated: dict[str, Any], specified: dict[str, Any]
) -> None:
    ignored_class_meta = {
        *("$$target", "$comment", "$defs", "$id", "$schema"),  # skip "$" fields
        "properties",  # checked in other tests
    }
    generated_meta = {k: v for k, v in generated.items() if k not in ignored_class_meta}
    specified_meta = {k: v for k, v in specified.items() if k not in ignored_class_meta}
    assert generated_meta == specified_meta


def dissolve_single_item_lists(dct: dict[str, Any], key: str) -> None:
    # if a list in a dict value has just one item, dissolve it into the parent dict
    if len(dct[key]) == 1 and isinstance(dct[key][0], dict):
        dct.update(dct.pop(key)[0])


def sub_only_text(repl: Callable[[str], str], string: str) -> str:
    # substitute only the textual parts of a string, e.g. leave slashes alone
    return re.sub(r"([a-zA-Z_-]+)", lambda m: repl(m.group(0)), string)


def prepare_field(field: str, obj: list[Any] | dict[str, Any]) -> None:
    # prepare each item in a list (in-place)
    if isinstance(obj, list):
        for item in obj:
            prepare_field(field, item)
        obj[:] = [item for item in obj if item]
        return

    # discard comments and descriptions
    obj.pop("$comment", None)  # only in spec
    obj.pop("description", None)  # only in spec

    # discard title but save value for later
    title = obj.pop("title", field)  # only in generated

    # align reference paths
    # (the paths to referenced vocabularies and types differ between the models
    # and the specification, so we need to make sure they match before comparing)
    if obj.get("pattern") == IDENTIFIER_PATTERN:
        del obj["pattern"]
        del obj["type"]
        if field in ("identifier", "stableTargetId"):
            obj["$ref"] = "/schema/fields/identifier"
        else:
            obj["$ref"] = "/schema/entities/{}#/identifier".format(
                title.removesuffix("Identifier").removeprefix("Merged")
            )

    # align concept/enum annotations
    elif obj.get("$ref") == "/schema/entities/concept#/identifier":
        obj["pattern"] = VOCABULARY_PATTERN
        obj["type"] = "string"
        del obj["$ref"]

    # make sure all refs have paths in kebab-case
    # (the models use the class names, whereas the spec uses kebab-case URLs)
    if "$ref" in obj:
        obj["$ref"] = sub_only_text(dromedary_to_kebab, obj["$ref"])

    # recurse into the field definitions for array items
    if obj.get("type") == "array":
        prepare_field(field, obj["items"])

    for quantifier in {"anyOf", "allOf"} & set(obj):
        # prepare choices
        prepare_field(field, obj[quantifier])
        # collapse non-choices
        dissolve_single_item_lists(obj, quantifier)


@pytest.mark.parametrize(
    ("entity_type", "field_name"),
    ENTITY_TYPES_AND_FIELD_NAMES_BY_FQN.values(),
    ids=ENTITY_TYPES_AND_FIELD_NAMES_BY_FQN.keys(),
)
def test_field_defs_match_spec(entity_type: str, field_name: str) -> None:
    specified_properties = SPECIFIED_SCHEMAS[entity_type]["properties"]
    generated_properties = GENERATED_SCHEMAS[entity_type]["properties"]
    specified = deepcopy(specified_properties[field_name])
    generated = deepcopy(generated_properties[field_name])

    prepare_field(field_name, specified)
    prepare_field(field_name, generated)

    assert generated == specified, f"""
{entity_type}.{field_name}

specified:
{json.dumps(specified_properties[field_name], indent=4, sort_keys=True)}

generated:
{json.dumps(generated_properties[field_name], indent=4, sort_keys=True)}
"""
