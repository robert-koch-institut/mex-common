from pydantic import Field

from mex.common.mapping.schema import (
    generate_entity_filter_schema,
    generate_mapping_schema_for_mex_class,
)
from mex.common.models import ExtractedData
from mex.common.types import OrganizationalUnitID
from mex.common.types.email import Email


class DummyClass(ExtractedData):
    dummy_identifier: OrganizationalUnitID | None = None  # not required
    dummy_str: str
    dummy_int: int | None = None  # not required
    dummy_email: Email
    dummy_list: list[str] = []  # not required
    dummy_min_length_list: list[str] = Field(min_length=1)


def test_entity_filter_schema() -> None:
    schema_model = generate_entity_filter_schema(DummyClass)

    expected = {
        "$defs": {
            "EntityFilter": {
                "additionalProperties": False,
                "description": "Entity filter model.",
                "properties": {
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/EntityFilterRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "EntityFilter",
                "type": "object",
            },
            "EntityFilterRule": {
                "additionalProperties": False,
                "description": "Entity filter rule model.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                },
                "title": "EntityFilterRule",
                "type": "object",
            },
        },
        "properties": {
            "DummyClass": {
                "default": None,
                "items": {"$ref": "#/$defs/EntityFilter"},
                "title": "Dummyclass",
                "type": "array",
            }
        },
        "title": "DummyClass",
        "type": "object",
    }

    assert schema_model.model_json_schema() == expected


def test_generate_mapping_schema() -> None:
    schema_model = generate_mapping_schema_for_mex_class(DummyClass)

    expected = {
        "$defs": {
            "Dummy_emailFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping schema "
                "for "
                "Dummy_email "
                "fields in "
                "primary "
                "source.",
                "properties": {
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/Dummy_emailMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "Dummy_emailFieldsInPrimarySource",
                "type": "object",
            },
            "Dummy_emailMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema of " "field Dummy_email.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                    "setValues": {
                        "anyOf": [
                            {
                                "items": {
                                    "examples": ["info@rki.de"],
                                    "format": "email",
                                    "pattern": "^[^@ "
                                    "\\t\\r\\n]+@[^@ "
                                    "\\t\\r\\n]+\\.[^@ "
                                    "\\t\\r\\n]+$",
                                    "title": "Email",
                                    "type": "string",
                                },
                                "type": "array",
                            },
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Setvalues",
                    },
                },
                "title": "Dummy_emailMappingRule",
                "type": "object",
            },
            "Dummy_identifierFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping "
                "schema "
                "for "
                "Dummy_identifier "
                "fields in "
                "primary "
                "source.",
                "properties": {
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/Dummy_identifierMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "Dummy_identifierFieldsInPrimarySource",
                "type": "object",
            },
            "Dummy_identifierMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema " "of field " "Dummy_identifier.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                    "setValues": {
                        "anyOf": [
                            {
                                "items": {
                                    "anyOf": [
                                        {
                                            "pattern": "^[a-zA-Z0-9]{14,22}$",
                                            "title": "OrganizationalUnitID",
                                            "type": "string",
                                        },
                                        {"type": "null"},
                                    ]
                                },
                                "type": "array",
                            },
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Setvalues",
                    },
                },
                "title": "Dummy_identifierMappingRule",
                "type": "object",
            },
            "Dummy_intFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping schema "
                "for Dummy_int "
                "fields in "
                "primary source.",
                "properties": {
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/Dummy_intMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "Dummy_intFieldsInPrimarySource",
                "type": "object",
            },
            "Dummy_intMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema of " "field Dummy_int.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                    "setValues": {
                        "anyOf": [
                            {
                                "items": {
                                    "anyOf": [{"type": "integer"}, {"type": "null"}]
                                },
                                "type": "array",
                            },
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Setvalues",
                    },
                },
                "title": "Dummy_intMappingRule",
                "type": "object",
            },
            "Dummy_listFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping schema "
                "for Dummy_list "
                "fields in "
                "primary source.",
                "properties": {
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/Dummy_listMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "Dummy_listFieldsInPrimarySource",
                "type": "object",
            },
            "Dummy_listMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema of " "field Dummy_list.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                    "setValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Setvalues",
                    },
                },
                "title": "Dummy_listMappingRule",
                "type": "object",
            },
            "Dummy_min_length_listFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping "
                "schema "
                "for "
                "Dummy_min_length_list "
                "fields "
                "in "
                "primary "
                "source.",
                "properties": {
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/Dummy_min_length_listMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "Dummy_min_length_listFieldsInPrimarySource",
                "type": "object",
            },
            "Dummy_min_length_listMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule "
                "schema of "
                "field "
                "Dummy_min_length_list.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                    "setValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Setvalues",
                    },
                },
                "title": "Dummy_min_length_listMappingRule",
                "type": "object",
            },
            "Dummy_strFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping schema "
                "for Dummy_str "
                "fields in "
                "primary source.",
                "properties": {
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/Dummy_strMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "Dummy_strFieldsInPrimarySource",
                "type": "object",
            },
            "Dummy_strMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema of " "field Dummy_str.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                    "setValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Setvalues",
                    },
                },
                "title": "Dummy_strMappingRule",
                "type": "object",
            },
            "HadprimarysourceFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping "
                "schema "
                "for "
                "Hadprimarysource "
                "fields in "
                "primary "
                "source.",
                "properties": {
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/HadprimarysourceMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "HadprimarysourceFieldsInPrimarySource",
                "type": "object",
            },
            "HadprimarysourceMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema " "of field " "Hadprimarysource.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                    "setValues": {
                        "anyOf": [
                            {
                                "items": {
                                    "pattern": "^[a-zA-Z0-9]{14,22}$",
                                    "title": "PrimarySourceID",
                                    "type": "string",
                                },
                                "type": "array",
                            },
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Setvalues",
                    },
                },
                "title": "HadprimarysourceMappingRule",
                "type": "object",
            },
            "IdentifierFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping schema "
                "for Identifier "
                "fields in "
                "primary source.",
                "properties": {
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/IdentifierMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "IdentifierFieldsInPrimarySource",
                "type": "object",
            },
            "IdentifierMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema of " "field Identifier.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                    "setValues": {
                        "anyOf": [
                            {
                                "items": {
                                    "pattern": "^[a-zA-Z0-9]{14,22}$",
                                    "title": "Identifier",
                                    "type": "string",
                                },
                                "type": "array",
                            },
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Setvalues",
                    },
                },
                "title": "IdentifierMappingRule",
                "type": "object",
            },
            "IdentifierinprimarysourceFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping "
                "schema "
                "for "
                "Identifierinprimarysource "
                "fields "
                "in "
                "primary "
                "source.",
                "properties": {
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "mappingRules": {
                        "items": {
                            "$ref": "#/$defs/IdentifierinprimarysourceMappingRule"
                        },
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "IdentifierinprimarysourceFieldsInPrimarySource",
                "type": "object",
            },
            "IdentifierinprimarysourceMappingRule": {
                "additionalProperties": False,
                "description": "Mapping "
                "rule "
                "schema of "
                "field "
                "Identifierinprimarysource.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                    "setValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Setvalues",
                    },
                },
                "title": "IdentifierinprimarysourceMappingRule",
                "type": "object",
            },
        },
        "description": "Schema for mapping the properties of the entity type "
        "DummyClass.",
        "properties": {
            "dummy_email": {
                "items": {"$ref": "#/$defs/Dummy_emailFieldsInPrimarySource"},
                "title": "Dummy Email",
                "type": "array",
            },
            "dummy_identifier": {
                "default": None,
                "items": {"$ref": "#/$defs/Dummy_identifierFieldsInPrimarySource"},
                "title": "Dummy Identifier",
                "type": "array",
            },
            "dummy_int": {
                "default": None,
                "items": {"$ref": "#/$defs/Dummy_intFieldsInPrimarySource"},
                "title": "Dummy Int",
                "type": "array",
            },
            "dummy_list": {
                "default": None,
                "items": {"$ref": "#/$defs/Dummy_listFieldsInPrimarySource"},
                "title": "Dummy List",
                "type": "array",
            },
            "dummy_min_length_list": {
                "items": {"$ref": "#/$defs/Dummy_min_length_listFieldsInPrimarySource"},
                "title": "Dummy Min Length List",
                "type": "array",
            },
            "dummy_str": {
                "items": {"$ref": "#/$defs/Dummy_strFieldsInPrimarySource"},
                "title": "Dummy Str",
                "type": "array",
            },
            "hadPrimarySource": {
                "items": {"$ref": "#/$defs/HadprimarysourceFieldsInPrimarySource"},
                "title": "Hadprimarysource",
                "type": "array",
            },
            "identifier": {
                "items": {"$ref": "#/$defs/IdentifierFieldsInPrimarySource"},
                "title": "Identifier",
                "type": "array",
            },
            "identifierInPrimarySource": {
                "items": {
                    "$ref": "#/$defs/IdentifierinprimarysourceFieldsInPrimarySource"
                },
                "title": "Identifierinprimarysource",
                "type": "array",
            },
        },
        "required": [
            "identifier",
            "hadPrimarySource",
            "identifierInPrimarySource",
            "dummy_str",
            "dummy_email",
            "dummy_min_length_list",
        ],
        "title": "DummyClass",
        "type": "object",
    }

    assert schema_model.model_json_schema() == expected
