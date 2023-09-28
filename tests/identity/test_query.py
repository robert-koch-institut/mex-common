import pytest
from pytest import MonkeyPatch

from mex.common.exceptions import MExError
from mex.common.identity.query import fetch_identity, upsert_identity
from mex.common.settings import BaseSettings
from mex.common.testing import Joker
from mex.common.types.identifier import Identifier, PrimarySourceID


def test_upsert_identity() -> None:
    system_a_id = PrimarySourceID.generate()
    old_target_id = Identifier.generate()
    new_target_id = Identifier.generate()
    identity_after_insert = upsert_identity(
        system_a_id, "thing-1", old_target_id, "type-x"
    )

    assert identity_after_insert.model_dump() == dict(
        hadPrimarySource=system_a_id,
        identifierInPrimarySource="thing-1",
        stableTargetId=old_target_id,
        entityType="type-x",
        identifier=Joker(),
    )

    identity_after_update = upsert_identity(
        system_a_id, "thing-1", new_target_id, "type-x"
    )

    assert identity_after_update.model_dump() == dict(
        hadPrimarySource=system_a_id,
        identifierInPrimarySource="thing-1",
        stableTargetId=new_target_id,
        entityType="type-x",
        identifier=Joker(),
    )


def test_unsupported_providers(monkeypatch: MonkeyPatch) -> None:
    settings = BaseSettings.get()
    monkeypatch.setattr(BaseSettings, "__setattr__", object.__setattr__)
    monkeypatch.setattr(settings, "identity_provider", "bogus-provider")

    with pytest.raises(MExError, match="Cannot fetch identity from bogus-provider."):
        fetch_identity()

    with pytest.raises(MExError, match="Cannot upsert identity to bogus-provider."):
        upsert_identity(
            PrimarySourceID.generate(), "thing-1", Identifier.generate(), "type-x"
        )


def test_fetch_identity() -> None:
    system_a_id = PrimarySourceID.generate()
    entity_1 = Identifier.generate()

    result = fetch_identity()
    assert result is None

    identity = upsert_identity(system_a_id, "thing-1", entity_1, "type-x")

    result = fetch_identity(
        had_primary_source=identity.hadPrimarySource,
        identifier_in_primary_source=identity.identifierInPrimarySource,
        stable_target_id=identity.stableTargetId,
    )
    assert result == identity


def test_fetch_identity_nothing_found() -> None:
    result = fetch_identity(
        had_primary_source=PrimarySourceID.generate(),
        identifier_in_primary_source=Identifier.generate(),
        stable_target_id=Identifier.generate(),
    )
    assert result is None
