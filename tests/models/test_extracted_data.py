from enum import Enum
from uuid import uuid4

import pytest
from pydantic import ValidationError

from mex.common.identity.connector import IdentityConnector
from mex.common.models.base import BaseModel
from mex.common.models.extracted_data import ExtractedData
from mex.common.types import Identifier


class Animal(Enum):
    """Dummy enum to use in tests."""

    CAT = "cat"
    DOG = "dog"


class BaseThing(BaseModel):
    """Dummy model defining a generic stableTargetId."""

    stableTargetId: Identifier


class ExtractedThing(BaseThing, ExtractedData):
    """Extracted version of a dummy thing model."""


def test_extracted_data_requires_identifier_in_primary_source() -> None:
    with pytest.raises(ValidationError, match="identifierInPrimarySource"):
        ExtractedThing(
            hadPrimarySource=Identifier.generate(seed=1),
        )


def test_extracted_data_requires_hadPrimarySource() -> None:
    with pytest.raises(ValidationError, match="hadPrimarySource"):
        ExtractedThing(
            identifierInPrimarySource="0",
        )


def test_extracted_data_does_not_allow_custom_identifiers() -> None:
    with pytest.raises(ValidationError, match="Identifier not found"):
        ExtractedThing(
            identifier=uuid4(),
            hadPrimarySource=Identifier.generate(seed=1),
            identifierInPrimarySource="0",
        )


def test_extracted_data_does_not_allow_altered_identities() -> None:
    extracted_data = ExtractedThing(
        hadPrimarySource=Identifier.generate(seed=1),
        identifierInPrimarySource="this",
    )

    with pytest.raises(ValidationError, match="Identifier not found"):
        ExtractedThing(
            identifier=extracted_data.identifier,
            hadPrimarySource=Identifier.generate(seed=1),
            identifierInPrimarySource="that",
        )


def test_extracted_data_does_allow_setting_preexisting_identifiers() -> None:
    extracted_data_1 = ExtractedThing(
        hadPrimarySource=Identifier.generate(seed=1),
        identifierInPrimarySource="0",
    )
    extracted_data_2 = ExtractedThing(
        identifier=extracted_data_1.identifier,
        hadPrimarySource=Identifier.generate(seed=1),
        identifierInPrimarySource="0",
    )

    assert extracted_data_1.identifier == extracted_data_2.identifier


def test_extracted_data_get_entity_type() -> None:
    assert ExtractedThing.get_entity_type() == "ExtractedThing"


def test_entity_merged_id() -> None:
    identity_connector = IdentityConnector.get()

    thing = ExtractedThing(
        identifierInPrimarySource="123",
        hadPrimarySource=Identifier.generate(seed=1),
    )

    identity = identity_connector.fetch(
        had_primary_source=thing.hadPrimarySource,
        identifier_in_primary_source=thing.identifierInPrimarySource,
    )
    assert identity is not None
    assert str(thing.stableTargetId) == identity.merged_id
