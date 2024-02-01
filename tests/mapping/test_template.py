from copy import deepcopy

from mex.ops.mapping.template import __create_template_from_schema, add_default_values


def test_create_template_from_dummy_json_schema() -> None:
    schema = {
        "type": "object",
        "properties": {
            "dummy_str": {"type": "string"},
            "dummy_url": {
                "title": "Url",
                "minLength": 1,
                "pattern": "^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\\\\?([^#]*))?(#(.*))?",
                "format": "uri",
            },
            "dummy_list": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "dummy_nested_bool": {"type": "boolean"},
                        "dummy_nested_string": {"type": "string"},
                    },
                    "required": ["dummy_nested_bool"],
                },
            },
            "dummy_choice": {"anyOf": [{"type": "integer"}, {"type": "string"}]},
        },
        "required": ["dummy_str"],
    }

    expected_template = {
        "dummy_str": None,
        "dummy_url": None,
        "dummy_list": [{"dummy_nested_bool": None, "dummy_nested_string": None}],
        "dummy_choice": None,
    }

    template = __create_template_from_schema(schema)
    assert template == expected_template


def test_add_default_values() -> None:
    standard_fields = {
        "fieldInPrimarySource": None,
        "locationInPrimarySource": None,
        "examplesInPrimarySource": [None],
        "mappingRules": [{"forValues": [None], "setValues": [None], "rule": None}],
        "comment": None,
    }
    original_template = {
        "identifier": [deepcopy(standard_fields)],
        "hadPrimarySource": [deepcopy(standard_fields)],
        "stableTargetId": [deepcopy(standard_fields)],
        "otherProperty": [deepcopy(standard_fields)],
    }
    default_value_template = add_default_values(original_template)
    assert default_value_template["otherProperty"] == original_template["otherProperty"]
    assert default_value_template["identifier"] == [
        {
            "fieldInPrimarySource": "n/a",
            "mappingRules": [{"rule": "Assign identifier."}],
        }
    ]
    assert default_value_template["hadPrimarySource"] == [
        {
            "fieldInPrimarySource": "n/a",
            "mappingRules": [
                {
                    "rule": "Assign 'stable target id' of primary source "
                    "with identifier '...' in "
                    "/raw-data/primary-sources/primary-sources.json."
                }
            ],
        }
    ]
    assert default_value_template["stableTargetId"] == [
        {
            "fieldInPrimarySource": "n/a",
            "mappingRules": [{"rule": "Assign 'stable target id' of merged item."}],
        }
    ]
