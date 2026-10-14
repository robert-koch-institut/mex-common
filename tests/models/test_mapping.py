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
    ("rule", "value_in_primary_source", "expected"),
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
        "value in forValues",
        "value not in forValues",
        "empty value not in forValues",
        "matching rule without setValues",
        "static rule is ignored",
        "empty forValues is ignored",
        "empty rule",
    ],
)
def test_mapping_rule_get_mapped_values(
    rule: MappingRule[str], value_in_primary_source: str, expected: str | None
) -> None:
    assert rule.get_mapped_values(value_in_primary_source) == expected


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
    ("value_in_primary_source", "expected"),
    [
        ("a", ["first", "second"]),
        ("b", ["second"]),
        ("c", ["fourth"]),
        ("x", []),
        ("", []),
    ],
    ids=[
        "all matching rules",
        "single matching rule",
        "skips matching rule without setValues",
        "no matching rule ignores static rule",
        "empty value",
    ],
)
def test_mapping_field_get_mapped_values(
    mapping_field: MappingField[str],
    value_in_primary_source: str,
    expected: list[str],
) -> None:
    assert mapping_field.get_mapped_values(value_in_primary_source) == expected


@pytest.mark.parametrize(
    ("field_in_primary_source", "location_in_primary_source", "expected"),
    [
        (None, None, ["first"]),
        ("kind", None, ["first"]),
        ("other", None, []),
        (None, "table", ["first"]),
        (None, "other", []),
        ("kind", "table", ["first"]),
        ("kind", "other", []),
    ],
    ids=[
        "no filters",
        "matching field",
        "non-matching field",
        "matching location",
        "non-matching location",
        "matching field and location",
        "matching field but non-matching location",
    ],
)
def test_mapping_field_get_mapped_values_filtered(
    field_in_primary_source: str | None,
    location_in_primary_source: str | None,
    expected: list[str],
) -> None:
    field = MappingField[str](
        fieldInPrimarySource="kind",
        locationInPrimarySource="table",
        mappingRules=[{"forValues": ["a"], "setValues": "first"}],
    )
    assert (
        field.get_mapped_values(
            "a",
            field_in_primary_source=field_in_primary_source,
            location_in_primary_source=location_in_primary_source,
        )
        == expected
    )


def test_mapping_rule_list_on_mapping_field(mapping_field: MappingField[str]) -> None:
    assert isinstance(mapping_field.mappingRules, MappingRuleList)
    assert mapping_field.mappingRules.get_mapped_values("a") == ["first", "second"]
    assert mapping_field.mappingRules.get_static_values() == "static"


def test_mapping_rule_list_flattens_list_values() -> None:
    rules = MappingRuleList[list[str]](
        [
            MappingRule[list[str]](forValues=["a"], setValues=["x", "y"]),
            MappingRule[list[str]](forValues=["a"]),
            MappingRule[list[str]](forValues=["a", "b"], setValues=["z"]),
        ]
    )
    assert rules.get_mapped_values("a") == ["x", "y", "z"]
    assert rules.get_mapped_values("b") == ["z"]


def test_mapping_rule_list_empty() -> None:
    assert MappingRuleList[str]().get_mapped_values("a") == []
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
                fieldInPrimarySource="kind",
                locationInPrimarySource="table",
                mappingRules=[{"forValues": ["a"], "setValues": "first"}],
            ),
            MappingField[str](mappingRules=[{"forValues": ["b"]}, {}]),
            MappingField[str](
                fieldInPrimarySource="type",
                locationInPrimarySource="table",
                mappingRules=[
                    {"forValues": ["a", "b"], "setValues": "third"},
                    {"setValues": "static"},
                ],
            ),
        ]
    )


@pytest.mark.parametrize(
    (
        "value_in_primary_source",
        "field_in_primary_source",
        "location_in_primary_source",
        "expected",
    ),
    [
        ("a", None, None, ["first", "third"]),
        ("b", None, None, ["third"]),
        ("x", None, None, []),
        ("", None, None, []),
        ("a", "kind", None, ["first"]),
        ("a", "type", None, ["third"]),
        ("a", None, "table", ["first", "third"]),
        ("a", "type", "table", ["third"]),
        ("a", "kind", "other", []),
        ("a", "missing", None, []),
    ],
    ids=[
        "all matching fields",
        "skips field without mapped value",
        "no matching field ignores static rule",
        "empty value",
        "filter by first field",
        "filter by last field",
        "filter by shared location",
        "filter by field and location",
        "non-matching location",
        "non-matching field",
    ],
)
def test_mapping_list_get_mapped_values(
    mapping_list: MappingFieldList[str],
    value_in_primary_source: str,
    field_in_primary_source: str | None,
    location_in_primary_source: str | None,
    expected: list[str],
) -> None:
    assert (
        mapping_list.get_mapped_values(
            value_in_primary_source,
            field_in_primary_source=field_in_primary_source,
            location_in_primary_source=location_in_primary_source,
        )
        == expected
    )


def test_mapping_list_get_static_values(mapping_list: MappingFieldList[str]) -> None:
    assert mapping_list.get_static_values() == "static"


def test_mapping_list_empty() -> None:
    assert MappingFieldList[str]().get_mapped_values("a") == []
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
    assert mapping.email.get_mapped_values("home") == []
    assert mapping.email.get_static_values() == ["info@example.com"]
    assert mapping.identifierInPrimarySource.get_static_values() == "cp-1"


@pytest.mark.parametrize(
    ("rule", "expected"),
    [
        (MappingRule[str](forValues=["a", "b"], setValues="foo"), ["a", "b"]),
        (MappingRule[str](forValues=["a"]), ["a"]),
        (MappingRule[str](forValues=[], setValues="foo"), []),
        (MappingRule[str](setValues="foo"), []),
    ],
    ids=[
        "rule with forValues",
        "rule without setValues",
        "empty forValues",
        "static rule",
    ],
)
def test_mapping_rule_get_mappable_values(
    rule: MappingRule[str], expected: list[str]
) -> None:
    assert rule.get_mappable_values() == expected


def test_mapping_rule_list_get_mappable_values(
    mapping_field: MappingField[str],
) -> None:
    assert mapping_field.mappingRules.get_mappable_values() == [
        "a",
        "a",
        "b",
        "c",
        "c",
        "d",
    ]
    assert MappingRuleList[str]().get_mappable_values() == []


@pytest.mark.parametrize(
    ("field_in_primary_source", "location_in_primary_source", "expected"),
    [
        (None, None, ["a", "b"]),
        ("kind", "table", ["a", "b"]),
        ("other", None, []),
        (None, "other", []),
    ],
    ids=[
        "no filters",
        "matching field and location",
        "non-matching field",
        "non-matching location",
    ],
)
def test_mapping_field_get_mappable_values(
    field_in_primary_source: str | None,
    location_in_primary_source: str | None,
    expected: list[str],
) -> None:
    field = MappingField[str](
        fieldInPrimarySource="kind",
        locationInPrimarySource="table",
        mappingRules=[
            {"forValues": ["a"], "setValues": "first"},
            {"forValues": ["b"]},
            {"setValues": "static"},
        ],
    )
    assert (
        field.get_mappable_values(
            field_in_primary_source=field_in_primary_source,
            location_in_primary_source=location_in_primary_source,
        )
        == expected
    )


@pytest.mark.parametrize(
    ("field_in_primary_source", "location_in_primary_source", "expected"),
    [
        (None, None, ["a", "b", "a", "b"]),
        ("kind", None, ["a"]),
        ("type", "table", ["a", "b"]),
        (None, "table", ["a", "a", "b"]),
        ("missing", None, []),
    ],
    ids=[
        "no filters",
        "filter by first field",
        "filter by field and location",
        "filter by shared location",
        "non-matching field",
    ],
)
def test_mapping_list_get_mappable_values(
    mapping_list: MappingFieldList[str],
    field_in_primary_source: str | None,
    location_in_primary_source: str | None,
    expected: list[str],
) -> None:
    assert (
        mapping_list.get_mappable_values(
            field_in_primary_source=field_in_primary_source,
            location_in_primary_source=location_in_primary_source,
        )
        == expected
    )
    assert MappingFieldList[str]().get_mappable_values() == []
