from mex.common.models import (
    EXTRACTED_MODEL_CLASSES,
    FILTER_MODEL_CLASSES,
    FilterField,
    PersonFilter,
)


def test_all_filter_classes_are_defined() -> None:
    stem_types = sorted(c.stemType for c in EXTRACTED_MODEL_CLASSES)
    assert sorted(c.stemType for c in FILTER_MODEL_CLASSES) == stem_types


def test_all_filter_fields_are_defined() -> None:
    for filter_cls in FILTER_MODEL_CLASSES:
        field_defs = {
            field_name: (field_info.annotation, field_info.default)
            for field_name, field_info in filter_cls.model_fields.items()
            if field_name != "entityType"
        }
        assert field_defs == {"fields": (list[FilterField], [])}


def test_filter_model_schema() -> None:
    assert PersonFilter.model_json_schema() == {
        "$defs": {
            "FilterField": {
                "additionalProperties": False,
                "description": "Filter definition for one field in the primary source.",
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
                    "filterRules": {
                        "items": {"$ref": "#/$defs/FilterRule"},
                        "minItems": 1,
                        "title": "filterRules",
                        "type": "array",
                    },
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "comment",
                    },
                },
                "required": ["filterRules"],
                "title": "FilterField",
                "type": "object",
            },
            "FilterRule": {
                "additionalProperties": False,
                "description": "A single filter rule to apply.",
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
                },
                "title": "FilterRule",
                "type": "object",
            },
        },
        "additionalProperties": False,
        "description": "Class for defining filter rules for person items.",
        "properties": {
            "$type": {
                "const": "PersonFilter",
                "default": "PersonFilter",
                "enum": ["PersonFilter"],
                "title": "$Type",
                "type": "string",
            },
            "fields": {
                "default": [],
                "items": {"$ref": "#/$defs/FilterField"},
                "title": "fields",
                "type": "array",
            },
        },
        "title": "PersonFilter",
        "type": "object",
    }
