from mex.common.identity.connector import IdentityConnector
from mex.common.testing import Joker
from mex.common.types.identifier import Identifier


def test_upsert_identity() -> None:
    connector = IdentityConnector.get()
    system_a_id = Identifier.generate()
    old_target_id = Identifier.generate()
    new_target_id = Identifier.generate()
    identity_after_insert = connector.upsert(
        system_a_id, "thing-1", old_target_id, "type-x"
    )

    assert identity_after_insert.dict() == dict(
        hadPrimarySource=system_a_id,
        identifierInPrimarySource="thing-1",
        stableTargetId=old_target_id,
        entityType="type-x",
        identifier=Joker(),
    )

    identity_after_update = connector.upsert(
        system_a_id, "thing-1", new_target_id, "type-x"
    )

    assert identity_after_update.dict() == dict(
        hadPrimarySource=system_a_id,
        identifierInPrimarySource="thing-1",
        stableTargetId=new_target_id,
        entityType="type-x",
        identifier=Joker(),
    )


def test_fetch_identity() -> None:
    connector = IdentityConnector.get()
    system_a_id = Identifier.generate()
    entity_1 = Identifier.generate()

    result = connector.fetch()
    assert result is None

    identity = connector.upsert(system_a_id, "thing-1", entity_1, "type-x")

    result = connector.fetch(
        had_primary_source=identity.platform_id,
        identifier_in_primary_source=identity.original_id,
        stable_target_id=identity.merged_id,
    )
    assert result == identity


def test_fetch_nothing_found() -> None:
    connector = IdentityConnector.get()

    result = connector.fetch(
        had_primary_source=Identifier.generate(),
        identifier_in_primary_source=Identifier.generate(),
        stable_target_id=Identifier.generate(),
    )
    assert result is None
