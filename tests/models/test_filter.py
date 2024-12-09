from typing import Annotated, ClassVar, Literal

from pydantic import Field

from mex.common.models import ExtractedData
from mex.common.models.base.filter import generate_entity_filter_schema
from mex.common.types import MergedOrganizationalUnitIdentifier
from mex.common.types.email import Email


class ExtractedDummy(ExtractedData):
    stemType: ClassVar[Annotated[Literal["Dummy"], Field(frozen=True)]] = "Dummy"
    entityType: Annotated[
        Literal["ExtractedDummy"], Field(alias="$type", frozen=True)
    ] = "ExtractedDummy"
    dummy_identifier: MergedOrganizationalUnitIdentifier | None = None  # not required
    dummy_str: str
    dummy_int: int | None = None  # not required
    dummy_email: Email
    dummy_list: list[str] = []  # not required
    dummy_min_length_list: Annotated[list[str], Field(min_length=1)]


def test_entity_filter_schema() -> None:
    schema_model = generate_entity_filter_schema(ExtractedDummy)

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
        "description": "Schema for entity filters for the entity type ExtractedDummy.",
        "properties": {
            "ExtractedDummy": {
                "default": None,
                "items": {"$ref": "#/$defs/EntityFilter"},
                "title": "Extracteddummy",
                "type": "array",
            }
        },
        "title": "DummyEntityFilter",
        "type": "object",
    }

    assert schema_model.model_json_schema() == expected
