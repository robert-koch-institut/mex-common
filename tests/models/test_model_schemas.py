import json
from copy import deepcopy
from itertools import zip_longest
from typing import Any

import pytest

from mex.common.transform import split_to_camel
from tests.models.conftest import (
    ENTITY_TYPES_AND_FIELD_NAMES_BY_FQN,
    GENERATED_SCHEMAS,
    SPECIFIED_SCHEMAS,
    prepare_generated_field,
    prepare_specified_field,
)


def test_entity_types_match_spec() -> None:
    assert list(GENERATED_SCHEMAS) == list(SPECIFIED_SCHEMAS)


@pytest.mark.parametrize(
    ("generated", "specified"),
    zip_longest(
        GENERATED_SCHEMAS.values(),
        SPECIFIED_SCHEMAS.values(),
        fillvalue={},
    ),
    ids=map(
        str,
        zip_longest(GENERATED_SCHEMAS, SPECIFIED_SCHEMAS, fillvalue="N/A"),
    ),
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
    zip_longest(
        GENERATED_SCHEMAS.values(),
        SPECIFIED_SCHEMAS.values(),
        fillvalue={},
    ),
    ids=map(
        str,
        zip_longest(GENERATED_SCHEMAS, SPECIFIED_SCHEMAS, fillvalue="N/A"),
    ),
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

    prepare_specified_field(field_name, specified)
    prepare_generated_field(field_name, generated)

    assert generated == specified, f"""
{split_to_camel(entity_type)}.{field_name}

specified:
{json.dumps(specified_properties[field_name], indent=4, sort_keys=True)}

generated:
{json.dumps(generated_properties[field_name], indent=4, sort_keys=True)}
"""
