from typing import Annotated, ClassVar, Literal

from pydantic import Field

from mex.common.models import ExtractedData
from mex.common.models.base.mapping import generate_mapping_schema
from mex.common.types import Email, Identifier, MergedOrganizationalUnitIdentifier


class ExtractedDummyIdentifier(Identifier):
    pass


class MergedDummyIdentifier(Identifier):
    pass


class ExtractedDummy(ExtractedData):
    stemType: ClassVar[Annotated[Literal["Dummy"], Field(frozen=True)]] = "Dummy"
    entityType: Annotated[
        Literal["ExtractedDummy"], Field(alias="$type", frozen=True)
    ] = "ExtractedDummy"
    identifier: Annotated[ExtractedDummyIdentifier, Field(frozen=True)]
    stableTargetId: MergedDummyIdentifier
    dummy_unit: MergedOrganizationalUnitIdentifier | None = None  # not required
    dummy_str: str
    dummy_int: int | None = None  # not required
    dummy_email: Email
    dummy_list: list[str] = []  # not required
    dummy_min_length_list: Annotated[list[str], Field(min_length=1)]


def test_generate_mapping_schema() -> None:
    schema_model = generate_mapping_schema(ExtractedDummy)

    expected = {
        "$defs": {
            "Dummy_emailFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping schema for Dummy_email fields in primary source.",
                "properties": {
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/Dummy_emailMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "Dummy_emailFieldsInPrimarySource",
                "type": "object",
            },
            "Dummy_emailMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema of field Dummy_email.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "setValues": {
                        "anyOf": [
                            {
                                "items": {
                                    "examples": ["info@rki.de"],
                                    "format": "email",
                                    "pattern": "^[^@ \\t\\r\\n]+@[^@ \\t\\r\\n]+\\.[^@ \\t\\r\\n]+$",
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
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                },
                "title": "Dummy_emailMappingRule",
                "type": "object",
            },
            "Dummy_intFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping schema for Dummy_int fields in primary source.",
                "properties": {
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/Dummy_intMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "Dummy_intFieldsInPrimarySource",
                "type": "object",
            },
            "Dummy_intMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema of field Dummy_int.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
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
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                },
                "title": "Dummy_intMappingRule",
                "type": "object",
            },
            "Dummy_listFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping schema for Dummy_list fields in primary source.",
                "properties": {
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/Dummy_listMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "Dummy_listFieldsInPrimarySource",
                "type": "object",
            },
            "Dummy_listMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema of field Dummy_list.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "setValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Setvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                },
                "title": "Dummy_listMappingRule",
                "type": "object",
            },
            "Dummy_min_length_listFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping schema for Dummy_min_length_list fields in primary source.",
                "properties": {
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/Dummy_min_length_listMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "Dummy_min_length_listFieldsInPrimarySource",
                "type": "object",
            },
            "Dummy_min_length_listMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema of field Dummy_min_length_list.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "setValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Setvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                },
                "title": "Dummy_min_length_listMappingRule",
                "type": "object",
            },
            "Dummy_strFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping schema for Dummy_str fields in primary source.",
                "properties": {
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/Dummy_strMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "Dummy_strFieldsInPrimarySource",
                "type": "object",
            },
            "Dummy_strMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema of field Dummy_str.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "setValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Setvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                },
                "title": "Dummy_strMappingRule",
                "type": "object",
            },
            "Dummy_unitFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping schema for Dummy_unit fields in primary source.",
                "properties": {
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/Dummy_unitMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "Dummy_unitFieldsInPrimarySource",
                "type": "object",
            },
            "Dummy_unitMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema of field Dummy_unit.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "setValues": {
                        "anyOf": [
                            {
                                "items": {
                                    "anyOf": [
                                        {
                                            "pattern": "^[a-zA-Z0-9]{14,22}$",
                                            "title": "MergedOrganizationalUnitIdentifier",
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
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                },
                "title": "Dummy_unitMappingRule",
                "type": "object",
            },
            "HadprimarysourceFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping schema for Hadprimarysource fields in primary source.",
                "properties": {
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/HadprimarysourceMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "HadprimarysourceFieldsInPrimarySource",
                "type": "object",
            },
            "HadprimarysourceMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema of field Hadprimarysource.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
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
                        "title": "Setvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                },
                "title": "HadprimarysourceMappingRule",
                "type": "object",
            },
            "IdentifierFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping schema for Identifier fields in primary source.",
                "properties": {
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/IdentifierMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "IdentifierFieldsInPrimarySource",
                "type": "object",
            },
            "IdentifierMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema of field Identifier.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "setValues": {
                        "anyOf": [
                            {
                                "items": {
                                    "pattern": "^[a-zA-Z0-9]{14,22}$",
                                    "title": "ExtractedDummyIdentifier",
                                    "type": "string",
                                },
                                "type": "array",
                            },
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Setvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                },
                "title": "IdentifierMappingRule",
                "type": "object",
            },
            "IdentifierinprimarysourceFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping schema for Identifierinprimarysource fields in primary source.",
                "properties": {
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "mappingRules": {
                        "items": {
                            "$ref": "#/$defs/IdentifierinprimarysourceMappingRule"
                        },
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "IdentifierinprimarysourceFieldsInPrimarySource",
                "type": "object",
            },
            "IdentifierinprimarysourceMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema of field Identifierinprimarysource.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "setValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Setvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                },
                "title": "IdentifierinprimarysourceMappingRule",
                "type": "object",
            },
            "StabletargetidFieldsInPrimarySource": {
                "additionalProperties": False,
                "description": "Mapping schema for Stabletargetid fields in primary source.",
                "properties": {
                    "fieldInPrimarySource": {
                        "title": "Fieldinprimarysource",
                        "type": "string",
                    },
                    "locationInPrimarySource": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Locationinprimarysource",
                    },
                    "examplesInPrimarySource": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Examplesinprimarysource",
                    },
                    "mappingRules": {
                        "items": {"$ref": "#/$defs/StabletargetidMappingRule"},
                        "minItems": 1,
                        "title": "Mappingrules",
                        "type": "array",
                    },
                    "comment": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Comment",
                    },
                },
                "required": ["fieldInPrimarySource", "mappingRules"],
                "title": "StabletargetidFieldsInPrimarySource",
                "type": "object",
            },
            "StabletargetidMappingRule": {
                "additionalProperties": False,
                "description": "Mapping rule schema of field Stabletargetid.",
                "properties": {
                    "forValues": {
                        "anyOf": [
                            {"items": {"type": "string"}, "type": "array"},
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Forvalues",
                    },
                    "setValues": {
                        "anyOf": [
                            {
                                "items": {
                                    "pattern": "^[a-zA-Z0-9]{14,22}$",
                                    "title": "MergedDummyIdentifier",
                                    "type": "string",
                                },
                                "type": "array",
                            },
                            {"type": "null"},
                        ],
                        "default": None,
                        "title": "Setvalues",
                    },
                    "rule": {
                        "anyOf": [{"type": "string"}, {"type": "null"}],
                        "default": None,
                        "title": "Rule",
                    },
                },
                "title": "StabletargetidMappingRule",
                "type": "object",
            },
        },
        "description": "Schema for mapping the properties of the entity type ExtractedDummy.",
        "properties": {
            "hadPrimarySource": {
                "items": {"$ref": "#/$defs/HadprimarysourceFieldsInPrimarySource"},
                "title": "Hadprimarysource",
                "type": "array",
            },
            "identifierInPrimarySource": {
                "items": {
                    "$ref": "#/$defs/IdentifierinprimarysourceFieldsInPrimarySource"
                },
                "title": "Identifierinprimarysource",
                "type": "array",
            },
            "identifier": {
                "items": {"$ref": "#/$defs/IdentifierFieldsInPrimarySource"},
                "title": "Identifier",
                "type": "array",
            },
            "stableTargetId": {
                "items": {"$ref": "#/$defs/StabletargetidFieldsInPrimarySource"},
                "title": "Stabletargetid",
                "type": "array",
            },
            "dummy_unit": {
                "default": None,
                "items": {"$ref": "#/$defs/Dummy_unitFieldsInPrimarySource"},
                "title": "Dummy Unit",
                "type": "array",
            },
            "dummy_str": {
                "items": {"$ref": "#/$defs/Dummy_strFieldsInPrimarySource"},
                "title": "Dummy Str",
                "type": "array",
            },
            "dummy_int": {
                "default": None,
                "items": {"$ref": "#/$defs/Dummy_intFieldsInPrimarySource"},
                "title": "Dummy Int",
                "type": "array",
            },
            "dummy_email": {
                "items": {"$ref": "#/$defs/Dummy_emailFieldsInPrimarySource"},
                "title": "Dummy Email",
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
        },
        "required": [
            "hadPrimarySource",
            "identifierInPrimarySource",
            "identifier",
            "stableTargetId",
            "dummy_str",
            "dummy_email",
            "dummy_min_length_list",
        ],
        "title": "DummyMapping",
        "type": "object",
    }

    assert schema_model.model_json_schema() == expected
