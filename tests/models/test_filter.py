from mex.common.models import (
    EXTRACTED_MODEL_CLASSES,
    EXTRACTED_MODEL_CLASSES_BY_NAME,
    FILTER_MODEL_CLASSES,
    FilterField,
    PersonFilter,
)


def test_all_filter_classes_are_defined() -> None:
    stem_types = sorted(c.stemType for c in EXTRACTED_MODEL_CLASSES)
    assert sorted(c.stemType for c in FILTER_MODEL_CLASSES) == stem_types


def test_all_filter_fields_are_defined() -> None:
    for filter_cls in FILTER_MODEL_CLASSES:
        extracted_cls = EXTRACTED_MODEL_CLASSES_BY_NAME[
            f"Extracted{filter_cls.stemType}"
        ]
        assert set(filter_cls.model_fields) == set(extracted_cls.model_fields)
        field_defs = {
            field_name: (field_info.annotation, field_info.default)
            for field_name, field_info in filter_cls.model_fields.items()
            if field_name != "entityType"
        }
        assert all(
            (annotation, default) == (list[FilterField], [])
            for annotation, default in field_defs.values()
        )


def test_filter_model_schema() -> None:
    assert PersonFilter.model_json_schema() == {
        "$defs": {
            "FilterField": {
                "additionalProperties": False,
                "description": "Entity filter field model.",
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
                        "items": {"$ref": "#/$defs/FilterRule"},
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
                "title": "FilterField",
                "type": "object",
            },
            "FilterRule": {
                "additionalProperties": False,
                "description": "Entity filter rule model.",
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
            "hadPrimarySource": {
                "default": [],
                "items": {"$ref": "#/$defs/FilterField"},
                "title": "Hadprimarysource",
                "type": "array",
            },
            "identifierInPrimarySource": {
                "default": [],
                "items": {"$ref": "#/$defs/FilterField"},
                "title": "Identifierinprimarysource",
                "type": "array",
            },
            "affiliation": {
                "default": [],
                "items": {"$ref": "#/$defs/FilterField"},
                "title": "Affiliation",
                "type": "array",
            },
            "email": {
                "default": [],
                "items": {"$ref": "#/$defs/FilterField"},
                "title": "Email",
                "type": "array",
            },
            "familyName": {
                "default": [],
                "items": {"$ref": "#/$defs/FilterField"},
                "title": "Familyname",
                "type": "array",
            },
            "fullName": {
                "default": [],
                "items": {"$ref": "#/$defs/FilterField"},
                "title": "Fullname",
                "type": "array",
            },
            "givenName": {
                "default": [],
                "items": {"$ref": "#/$defs/FilterField"},
                "title": "Givenname",
                "type": "array",
            },
            "isniId": {
                "default": [],
                "items": {"$ref": "#/$defs/FilterField"},
                "title": "Isniid",
                "type": "array",
            },
            "memberOf": {
                "default": [],
                "items": {"$ref": "#/$defs/FilterField"},
                "title": "Memberof",
                "type": "array",
            },
            "orcidId": {
                "default": [],
                "items": {"$ref": "#/$defs/FilterField"},
                "title": "Orcidid",
                "type": "array",
            },
        },
        "title": "PersonFilter",
        "type": "object",
    }
