import glob
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from mex.common.models import EXTRACTED_MODEL_CLASSES_BY_NAME
from mex.common.transform import dromedary_to_kebab
from mex.common.types.identifier import MEX_ID_PATTERN, Identifier

# TODO: find a cleaner way to get to the mex-model JSON schemas
SPECIFIED_SCHEMA_PATH = Path(".venv", "src", "mex-model", "schema", "entities")

GENERATED_SCHEMAS = dict(
    sorted(
        {
            name.removeprefix("Extracted"): model.schema()
            for name, model in EXTRACTED_MODEL_CLASSES_BY_NAME.items()
        }.items()
    )
)
SPECIFIED_SCHEMAS = dict(
    sorted(
        {
            schema["title"].replace(" ", ""): schema
            for file_name in glob.glob(str(SPECIFIED_SCHEMA_PATH / "*.json"))
            if (schema := json.load(open(file_name)))
            and not schema["title"].startswith("Concept")
        }.items()
    )
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
    zip(GENERATED_SCHEMAS.values(), SPECIFIED_SCHEMAS.values()),
    ids=GENERATED_SCHEMAS,
)
def test_field_names_match_spec(
    generated: dict[str, Any], specified: dict[str, Any]
) -> None:
    assert set(generated["properties"]) == set(specified["properties"])


@pytest.mark.parametrize(
    ("generated", "specified"),
    zip(GENERATED_SCHEMAS.values(), SPECIFIED_SCHEMAS.values()),
    ids=GENERATED_SCHEMAS,
)
def test_required_fields_match_spec(
    generated: dict[str, Any], specified: dict[str, Any]
) -> None:
    assert set(generated["required"]) == set(specified["required"])


@pytest.mark.parametrize(
    ("entity_type", "field_name"),
    ENTITY_TYPES_AND_FIELD_NAMES_BY_FQN.values(),
    ids=ENTITY_TYPES_AND_FIELD_NAMES_BY_FQN.keys(),
)
def test_field_defs_match_spec(entity_type: str, field_name: str) -> None:  # noqa: C901
    def prepare_field(obj: list[Any] | dict[str, Any]) -> None:  # noqa: C901
        if isinstance(obj, list):
            for item in obj:
                prepare_field(item)
            return
        obj.pop("sameAs", None)
        obj.pop("subPropertyOf", None)
        obj.pop("description", None)
        if examples := obj.get("examples"):
            if isinstance(examples, list) and all(
                isinstance(e, Identifier) for e in examples
            ):
                obj.pop("examples")
        if obj.get("pattern") == MEX_ID_PATTERN:
            obj.pop("pattern")
            obj.pop("type")
            if obj.get("title") and field_name not in ("identifier", "stableTargetId"):
                title = dromedary_to_kebab(obj.pop("title").removesuffix("ID"))
                obj["$ref"] = f"/schema/entities/{title}#/identifier"
            else:
                obj["$ref"] = "/schema/fields/identifier"
        else:
            obj.pop("title", None)
        if "$ref" in obj:
            obj["$ref"] = (
                obj["$ref"].replace("#/definitions/", "/schema/fields/").lower()
            )
            if obj["$ref"] == "/schema/entities/concept#/identifier" and (
                scheme := obj.pop("useScheme", None)
            ):
                name = scheme.replace("-", "").removeprefix("https://mex.rki.de/item/")
                obj["$ref"] = f"/schema/fields/{name}"
        if obj.get("type") == "array":
            obj.pop("default", None)
            prepare_field(obj["items"])
        if "anyOf" in obj:
            obj["oneOf"] = obj.pop("anyOf")
        if "oneOf" in obj:
            prepare_field(obj["oneOf"])
        if "allOf" in obj:
            prepare_field(obj["allOf"])
            if len(obj["allOf"]) == 1:
                obj.update(obj.pop("allOf")[0])

    generated = deepcopy(GENERATED_SCHEMAS[entity_type]["properties"][field_name])
    specified = deepcopy(SPECIFIED_SCHEMAS[entity_type]["properties"][field_name])

    prepare_field(specified)
    prepare_field(generated)

    assert generated == specified
