from typing import get_origin

import pytest
from pydantic_core import PydanticUndefined

from mex.common.models import (
    EXTRACTED_MODEL_CLASSES,
    EXTRACTED_MODEL_CLASSES_BY_NAME,
    MAPPING_MODEL_CLASSES,
    ContactPointMapping,
    MappingField,
    MappingFieldList,
    MappingRule,
    MappingRuleList,
    VariableGroupMapping,
)


def test_all_mapping_classes_are_defined() -> None:
    stem_types = sorted(c.stemType for c in EXTRACTED_MODEL_CLASSES)
    assert sorted(c.stemType for c in MAPPING_MODEL_CLASSES) == stem_types


def test_all_mapping_fields_are_defined() -> None:
    for mapping_cls in MAPPING_MODEL_CLASSES:
        extracted_cls = EXTRACTED_MODEL_CLASSES_BY_NAME[
            f"Extracted{mapping_cls.stemType}"
        ]
        assert set(mapping_cls.model_fields) == set(extracted_cls.model_fields)
        field_defs = {
            field_name: (field_info.annotation, field_info.default)
            for field_name, field_info in mapping_cls.model_fields.items()
            if field_name != "entityType"
        }
        assert all(
            annotation is not None
            and get_origin(annotation) is MappingFieldList
            and default in (PydanticUndefined, [])
            for annotation, default in field_defs.values()
        )


def test_mapping_model_schema() -> None:
    assert VariableGroupMapping.model_json_schema() == {
        "$defs": {
            "MappingField_MergedPrimarySourceIdentifier_": {
                "additionalProperties": False,
                "properties": {
                    "fieldInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "fieldInPrimarySource",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "locationInPrimarySource",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "examplesInPrimarySource",
                    },
                    "mappingRules": {
                        "items": {
                            "$ref": "#/$defs/MappingRule_MergedPrimarySourceIdentifier_"
                        },
                        "minItems": 1,
                        "title": "mappingRules",
                        "type": "array",
                    },
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "comment",
                    },
                },
                "required": ["mappingRules"],
                "title": "MappingField[MergedPrimarySourceIdentifier]",
                "type": "object",
            },
            "MappingField_list_MergedResourceIdentifier__": {
                "additionalProperties": False,
                "properties": {
                    "fieldInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "fieldInPrimarySource",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "locationInPrimarySource",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "examplesInPrimarySource",
                    },
                    "mappingRules": {
                        "items": {
                            "$ref": "#/$defs/MappingRule_list_MergedResourceIdentifier__"
                        },
                        "minItems": 1,
                        "title": "mappingRules",
                        "type": "array",
                    },
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "comment",
                    },
                },
                "required": ["mappingRules"],
                "title": "MappingField[list[MergedResourceIdentifier]]",
                "type": "object",
            },
            "MappingField_list_Text__": {
                "additionalProperties": False,
                "properties": {
                    "fieldInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "fieldInPrimarySource",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "locationInPrimarySource",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "examplesInPrimarySource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/MappingRule_list_Text__"},
                        "minItems": 1,
                        "title": "mappingRules",
                        "type": "array",
                    },
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "comment",
                    },
                },
                "required": ["mappingRules"],
                "title": "MappingField[list[Text]]",
                "type": "object",
            },
            "MappingField_str_": {
                "additionalProperties": False,
                "properties": {
                    "fieldInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "fieldInPrimarySource",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "locationInPrimarySource",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "examplesInPrimarySource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/MappingRule_str_"},
                        "minItems": 1,
                        "title": "mappingRules",
                        "type": "array",
                    },
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "comment",
                    },
                },
                "required": ["mappingRules"],
                "title": "MappingField[str]",
                "type": "object",
            },
            "MappingRule_MergedPrimarySourceIdentifier_": {
                "additionalProperties": False,
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "forValues",
                    },
                    "setValues": {
                        "anyOf": [
                            {
                                "pattern": "^[a-zA-Z0-9]{14,22}$",
                                "title": "MergedPrimarySourceIdentifier",
                                "type": "string",
                            },
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "setValues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "rule",
                    },
                },
                "title": "MappingRule[MergedPrimarySourceIdentifier]",
                "type": "object",
            },
            "MappingRule_list_MergedResourceIdentifier__": {
                "additionalProperties": False,
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "forValues",
                    },
                    "setValues": {
                        "anyOf": [
                            {
                                "items": {
                                    "pattern": "^[a-zA-Z0-9]{14,22}$",
                                    "title": "MergedResourceIdentifier",
                                    "type": "string",
                                },
                                "type": "array",
                            },
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "setValues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "rule",
                    },
                },
                "title": "MappingRule[list[MergedResourceIdentifier]]",
                "type": "object",
            },
            "MappingRule_list_Text__": {
                "additionalProperties": False,
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "forValues",
                    },
                    "setValues": {
                        "anyOf": [
                            {"items": {"$ref": "#/$defs/Text"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "setValues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "rule",
                    },
                },
                "title": "MappingRule[list[Text]]",
                "type": "object",
            },
            "MappingRule_str_": {
                "additionalProperties": False,
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "forValues",
                    },
                    "setValues": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "setValues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "rule",
                    },
                },
                "title": "MappingRule[str]",
                "type": "object",
            },
            "Text": {
                "description": 'Type class for text objects.\n\nTexts can be parsed from nested JSON objects or from raw strings.\n\nExample:\n    Text(value="foo") == Text.model_validate("foo")',
                "properties": {
                    "value": {"minLength": 1, "title": "Value", "type": "string"},
                    "language": {
                        "anyOf": [{"$ref": "#/$defs/TextLanguage"}, {"type": "null"}],
                        "default": None,
                    },
                },
                "required": ["value"],
                "title": "Text",
                "type": "object",
            },
            "TextLanguage": {
                "description": "Possible language tags for `Text` values.",
                "enum": ["de", "en", "fr", "es", "ru"],
                "title": "TextLanguage",
                "type": "string",
            },
        },
        "additionalProperties": False,
        "description": "Mapping for describing a variable group transformation.",
        "properties": {
            "$type": {
                "const": "VariableGroupMapping",
                "default": "VariableGroupMapping",
                "title": "$Type",
                "type": "string",
            },
            "hadPrimarySource": {
                "items": {
                    "$ref": "#/$defs/MappingField_MergedPrimarySourceIdentifier_"
                },
                "minItems": 1,
                "title": "Hadprimarysource",
                "type": "array",
            },
            "identifierInPrimarySource": {
                "items": {"$ref": "#/$defs/MappingField_str_"},
                "minItems": 1,
                "title": "Identifierinprimarysource",
                "type": "array",
            },
            "containedBy": {
                "items": {
                    "$ref": "#/$defs/MappingField_list_MergedResourceIdentifier__"
                },
                "minItems": 1,
                "title": "Containedby",
                "type": "array",
            },
            "label": {
                "items": {"$ref": "#/$defs/MappingField_list_Text__"},
                "minItems": 1,
                "title": "Label",
                "type": "array",
            },
        },
        "required": [
            "hadPrimarySource",
            "identifierInPrimarySource",
            "containedBy",
            "label",
        ],
        "title": "VariableGroupMapping",
        "type": "object",
    }


@pytest.mark.parametrize(
    ("rule", "input_value", "expected"),
    [
        (MappingRule[str](forValues=["a", "b"], setValues="foo"), "b", "foo"),
        (MappingRule[str](forValues=["a", "b"], setValues="foo"), "c", None),
        (MappingRule[str](forValues=["a"], setValues="foo"), "", None),
        (MappingRule[str](forValues=["a"]), "a", None),
        (MappingRule[str](setValues="foo"), "a", None),
        (MappingRule[str](forValues=[], setValues="foo"), "a", None),
        (MappingRule[str](), "a", None),
    ],
    ids=[
        "input in forValues",
        "input not in forValues",
        "empty input not in forValues",
        "matching rule without setValues",
        "static rule is ignored",
        "empty forValues is ignored",
        "empty rule",
    ],
)
def test_mapping_rule_get_mapped_values(
    rule: MappingRule[str], input_value: str, expected: str | None
) -> None:
    assert rule.get_mapped_values(input_value) == expected


@pytest.mark.parametrize(
    ("rule", "expected"),
    [
        (MappingRule[str](setValues="foo"), "foo"),
        (MappingRule[str](forValues=[], setValues="foo"), "foo"),
        (MappingRule[str](forValues=["a"], setValues="foo"), None),
        (MappingRule[str](), None),
    ],
    ids=[
        "no forValues",
        "empty forValues",
        "rule with forValues is ignored",
        "empty rule",
    ],
)
def test_mapping_rule_get_static_values(
    rule: MappingRule[str], expected: str | None
) -> None:
    assert rule.get_static_values() == expected


@pytest.fixture
def mapping_field() -> MappingField[str]:
    return MappingField[str](
        mappingRules=[
            {"forValues": ["a"], "setValues": "first"},
            {"forValues": ["a", "b"], "setValues": "second"},
            {"forValues": ["c"]},
            {"forValues": ["c", "d"], "setValues": "fourth"},
            {},
            {"setValues": "static"},
        ]
    )


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ("a", "first"),
        ("b", "second"),
        ("c", "fourth"),
        ("x", None),
        ("", None),
    ],
    ids=[
        "first matching rule wins",
        "falls through to later rule",
        "skips matching rule without setValues",
        "no matching rule ignores static rule",
        "empty input",
    ],
)
def test_mapping_field_get_mapped_values(
    mapping_field: MappingField[str], input_value: str, expected: str | None
) -> None:
    assert mapping_field.get_mapped_values(input_value) == expected


def test_mapping_rule_list_on_mapping_field(mapping_field: MappingField[str]) -> None:
    assert isinstance(mapping_field.mappingRules, MappingRuleList)
    assert mapping_field.mappingRules.get_mapped_values("a") == "first"
    assert mapping_field.mappingRules.get_static_values() == "static"


def test_mapping_rule_list_empty() -> None:
    assert MappingRuleList[str]().get_mapped_values("a") is None
    assert MappingRuleList[str]().get_static_values() is None


def test_mapping_field_get_static_values(mapping_field: MappingField[str]) -> None:
    assert mapping_field.get_static_values() == "static"


def test_mapping_field_get_static_value_without_static_rule() -> None:
    field = MappingField[str](mappingRules=[{"forValues": ["a"], "setValues": "a"}])
    assert field.get_static_values() is None


@pytest.fixture
def mapping_list() -> MappingFieldList[str]:
    return MappingFieldList(
        [
            MappingField[str](
                mappingRules=[{"forValues": ["a"], "setValues": "first"}]
            ),
            MappingField[str](mappingRules=[{"forValues": ["b"]}, {}]),
            MappingField[str](
                mappingRules=[
                    {"forValues": ["a", "b"], "setValues": "third"},
                    {"setValues": "static"},
                ]
            ),
        ]
    )


@pytest.mark.parametrize(
    ("input_value", "expected"),
    [
        ("a", "first"),
        ("b", "third"),
        ("x", None),
        ("", None),
    ],
    ids=[
        "first matching field wins",
        "skips field without mapped value",
        "no matching field ignores static rule",
        "empty input",
    ],
)
def test_mapping_list_get_mapped_values(
    mapping_list: MappingFieldList[str], input_value: str, expected: str | None
) -> None:
    assert mapping_list.get_mapped_values(input_value) == expected


def test_mapping_list_get_static_values(mapping_list: MappingFieldList[str]) -> None:
    assert mapping_list.get_static_values() == "static"


def test_mapping_list_empty() -> None:
    assert MappingFieldList[str]().get_mapped_values("a") is None
    assert MappingFieldList[str]().get_static_values() is None


def test_mapping_list_on_mapping_model() -> None:
    mapping = ContactPointMapping(
        hadPrimarySource=[{"mappingRules": [{"setValues": "bFQoRhcVH5DHU6"}]}],
        identifierInPrimarySource=[{"mappingRules": [{"setValues": "cp-1"}]}],
        email=[
            {
                "mappingRules": [
                    {"forValues": ["work"], "setValues": ["work@example.com"]},
                    {"setValues": ["info@example.com"]},
                ]
            }
        ],
    )
    assert isinstance(mapping.email, MappingFieldList)
    assert mapping.email.get_mapped_values("work") == ["work@example.com"]
    assert mapping.email.get_mapped_values("home") is None
    assert mapping.email.get_static_values() == ["info@example.com"]
    assert mapping.identifierInPrimarySource.get_static_values() == "cp-1"
