from typing import get_origin

from pydantic_core import PydanticUndefined

from mex.common.models import (
    EXTRACTED_MODEL_CLASSES,
    EXTRACTED_MODEL_CLASSES_BY_NAME,
    MAPPING_MODEL_CLASSES,
    MappingField,
    VariableGroupMapping,
)
from mex.common.testing import Joker


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
            get_origin(annotation) is list
            and annotation.__args__[0].__bases__[0] is MappingField
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
                                "items": {
                                    "pattern": "^[a-zA-Z0-9]{14,22}$",
                                    "title": "MergedPrimarySourceIdentifier",
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
                                    "items": {
                                        "pattern": "^[a-zA-Z0-9]{14,22}$",
                                        "title": "MergedResourceIdentifier",
                                        "type": "string",
                                    },
                                    "type": "array",
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
                            {
                                "items": {
                                    "items": {"$ref": "#/$defs/Text"},
                                    "type": "array",
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
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
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
                "title": "MappingRule[str]",
                "type": "object",
            },
            "Text": {
                "description": Joker(),
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
                "enum": ["de", "en"],
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
                "enum": ["VariableGroupMapping"],
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
