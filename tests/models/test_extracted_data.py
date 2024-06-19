from enum import Enum
from typing import Annotated, Literal

import pytest
from pydantic import Field, ValidationError, computed_field

from mex.common.identity import get_provider
from mex.common.models import (
    MEX_PRIMARY_SOURCE_IDENTIFIER,
    MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE,
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    BaseModel,
    ExtractedData,
)
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

    @computed_field
    def identifier(self) -> ExtractedThingIdentifier:
        """Return the computed identifier for this extracted data item."""
        return self._get_identifier(ExtractedThingIdentifier)

    @identifier.setter  # type: ignore[no-redef]
    def identifier(self, obj: ExtractedThingIdentifier) -> None:
        """Set the identifier field to its pre-determined value."""
        return self._set_identifier(obj)

    @computed_field
    def stableTargetId(self) -> MergedThingIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted data item."""
        return self._get_stable_target_id(MergedThingIdentifier)

    @stableTargetId.setter  # type: ignore[no-redef]
    def stableTargetId(self, obj: MergedThingIdentifier) -> None:  # noqa: N802
        """Set the stableTargetId field to its pre-determined value."""
        return self._set_stable_target_id(obj)


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


def test_extracted_data_does_not_allow_setting_identifier() -> None:
    with pytest.raises(ValidationError, match="identifier cannot be changed"):
        ExtractedThing(
            identifier=Identifier.generate(seed=0),
            hadPrimarySource=MergedPrimarySourceIdentifier.generate(seed=1),
            identifierInPrimarySource="0",
        )


def test_extracted_data_does_allow_parsing_with_preexisting_identifiers() -> None:
    thing_1 = ExtractedThing(
        hadPrimarySource=MergedPrimarySourceIdentifier.generate(seed=1),
        identifierInPrimarySource="0",
    )
    thing_2 = ExtractedThing.model_validate(
        dict(
            identifier=thing_1.identifier,
            hadPrimarySource=MergedPrimarySourceIdentifier.generate(seed=1),
            identifierInPrimarySource="0",
        )
    )

    assert thing_1.identifier == thing_2.identifier


def test_extracted_data_does_not_allow_changing_mex_stable_target_id() -> None:
    with pytest.raises(ValidationError, match="stableTargetId cannot be changed"):
        ExtractedThing(
            identifier=MEX_PRIMARY_SOURCE_IDENTIFIER,
            hadPrimarySource=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
            identifierInPrimarySource=MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE,
            stableTargetId=MergedPrimarySourceIdentifier.generate(seed=12345),
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
