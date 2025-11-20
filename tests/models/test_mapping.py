from typing import get_origin

from pydantic_core import PydanticUndefined

from mex.common.models import (
    EXTRACTED_MODEL_CLASSES,
    EXTRACTED_MODEL_CLASSES_BY_NAME,
    MAPPING_MODEL_CLASSES,
    MappingField,
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
            and get_origin(annotation) is list
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
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "comment",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "examplesInPrimarySource",
                    },
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
                    "mappingRules": {
                        "items": {
                            "$ref": "#/$defs/MappingRule_MergedPrimarySourceIdentifier_"
                        },
                        "minItems": 1,
                        "title": "mappingRules",
                        "type": "array",
                    },
                },
                "required": ["mappingRules"],
                "title": "MappingField[MergedPrimarySourceIdentifier]",
                "type": "object",
            },
            "MappingField_list_MergedResourceIdentifier__": {
                "additionalProperties": False,
                "properties": {
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "comment",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "examplesInPrimarySource",
                    },
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
                    "mappingRules": {
                        "items": {
                            "$ref": "#/$defs/MappingRule_list_MergedResourceIdentifier__"
                        },
                        "minItems": 1,
                        "title": "mappingRules",
                        "type": "array",
                    },
                },
                "required": ["mappingRules"],
                "title": "MappingField[list[MergedResourceIdentifier]]",
                "type": "object",
            },
            "MappingField_list_Text__": {
                "additionalProperties": False,
                "properties": {
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "comment",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "examplesInPrimarySource",
                    },
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
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/MappingRule_list_Text__"},
                        "minItems": 1,
                        "title": "mappingRules",
                        "type": "array",
                    },
                },
                "required": ["mappingRules"],
                "title": "MappingField[list[Text]]",
                "type": "object",
            },
            "MappingField_str_": {
                "additionalProperties": False,
                "properties": {
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "comment",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "examplesInPrimarySource",
                    },
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
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/MappingRule_str_"},
                        "minItems": 1,
                        "title": "mappingRules",
                        "type": "array",
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
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "rule",
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
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "rule",
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
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "rule",
                    },
                    "setValues": {
                        "anyOf": [
                            {"items": {"$ref": "#/$defs/Text"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "setValues",
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
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "rule",
                    },
                    "setValues": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "setValues",
                    },
                },
                "title": "MappingRule[str]",
                "type": "object",
            },
            "RestrictedTextLanguage": {
                "description": "Allowes only English and "
                "German as language tags "
                "for `Text` values.",
                "enum": ["de", "en"],
                "title": "RestrictedTextLanguage",
                "type": "string",
            },
            "Text": {
                "description": "Type class for text objects.\n"
                "\n"
                "Texts can be parsed from nested JSON "
                "objects or from raw strings.\n"
                "\n"
                "Example:\n"
                '    Text(value="foo") == '
                'Text.model_validate("foo")',
                "properties": {
                    "language": {
                        "anyOf": [
                            {"$ref": "#/$defs/RestrictedTextLanguage"},
                            {"$ref": "#/$defs/TextLanguage"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Language",
                    },
                    "value": {"minLength": 1, "title": "Value", "type": "string"},
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
            "containedBy": {
                "items": {
                    "$ref": "#/$defs/MappingField_list_MergedResourceIdentifier__"
                },
                "minItems": 1,
                "title": "Containedby",
                "type": "array",
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
