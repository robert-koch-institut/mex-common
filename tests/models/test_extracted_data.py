from enum import Enum
from typing import Annotated, Literal

import pytest
from pydantic import Field, ValidationError, computed_field

from mex.common.identity import get_provider
from mex.common.models import BaseModel, ExtractedData
from mex.common.types import Identifier, MergedPrimarySourceIdentifier


class Animal(Enum):
    """Dummy enum to use in tests."""

    CAT = "cat"
    DOG = "dog"


class ExtractedThingIdentifier(Identifier):
    """Identifier for extracted things."""


class MergedThingIdentifier(Identifier):
    """Identifier for merged thing."""


class BaseThing(BaseModel):
    """Dummy model defining some arbitrary field."""

    someField: str = "someDefault"


class ExtractedThing(BaseThing, ExtractedData):
    """Extracted version of a dummy thing model."""

    entityType: Annotated[
        Literal["ExtractedThing"], Field(alias="$type", frozen=True)
    ] = "ExtractedThing"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(self) -> ExtractedThingIdentifier:
        """Return the computed identifier for this extracted data item."""
        return self._get_identifier(ExtractedThingIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedThingIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted data item."""
        return self._get_stable_target_id(MergedThingIdentifier)


def test_extracted_data_requires_dict_for_construction() -> None:
    with pytest.raises(ValidationError, match="Input should be a valid dictionary"):
        ExtractedThing.model_validate(["this is a list"])


def test_extracted_data_requires_identifier_in_primary_source() -> None:
    with pytest.raises(ValidationError, match="identifierInPrimarySource"):
        ExtractedThing(
            hadPrimarySource=MergedPrimarySourceIdentifier.generate(seed=1),
        )


def test_extracted_data_requires_had_primary_source() -> None:
    with pytest.raises(ValidationError, match="hadPrimarySource"):
        ExtractedThing(
            identifierInPrimarySource="0",
        )


def test_extracted_data_stores_identity_in_provider() -> None:
    thing = ExtractedThing(
        identifierInPrimarySource="12345",
        hadPrimarySource=MergedPrimarySourceIdentifier.generate(seed=12345),
    )
    assert thing.identifier
    assert thing.stableTargetId

    provider = get_provider()
    identities = provider.fetch(
        had_primary_source=thing.hadPrimarySource,
        identifier_in_primary_source=thing.identifierInPrimarySource,
    )
    assert len(identities) == 1
    assert str(thing.identifier) == identities[0].identifier
    assert str(thing.stableTargetId) == identities[0].stableTargetId


def test_hash_function():
    hps1 = MergedPrimarySourceIdentifier.generate(seed=123456)
    hps2 = MergedPrimarySourceIdentifier.generate(seed=234567)
    thing1 = ExtractedThing(hadPrimarySource=hps1, identifierInPrimarySource="4567")
    thing2 = ExtractedThing(hadPrimarySource=hps1, identifierInPrimarySource="4567")
    thing3 = ExtractedThing(hadPrimarySource=hps2, identifierInPrimarySource="567")

    assert hash(thing1) == hash(thing2)
    assert hash(thing1) != hash(thing3)
