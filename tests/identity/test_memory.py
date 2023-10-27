from mex.common.identity.memory import MemoryIdentityProvider
from mex.common.testing import Joker
from mex.common.types import PrimarySourceID


def test_assign() -> None:
    provider = MemoryIdentityProvider.get()
    had_primary_source = PrimarySourceID("00000000000000")
    identifier_in_primary_source = "thing-1"

    new_identity = provider.assign(had_primary_source, identifier_in_primary_source)

    assert new_identity.dict() == dict(
        hadPrimarySource=had_primary_source,
        identifierInPrimarySource=identifier_in_primary_source,
        stableTargetId=Joker(),
        identifier=Joker(),
    )

    found_identity = provider.assign(had_primary_source, identifier_in_primary_source)

    assert found_identity.dict() == dict(
        hadPrimarySource=had_primary_source,
        identifierInPrimarySource=identifier_in_primary_source,
        stableTargetId=new_identity.stableTargetId,
        identifier=new_identity.identifier,
    )


def test_fetch_empty() -> None:
    provider = MemoryIdentityProvider.get()
    had_primary_source = PrimarySourceID("00000000000000")
    identifier_in_primary_source = "thing-1"

    # fetch something that the provider does not know
    identities = provider.fetch(
        had_primary_source=had_primary_source,
        identifier_in_primary_source=identifier_in_primary_source,
    )
    # we get an empty identity list
    assert not identities


def test_fetch_found() -> None:
    provider = MemoryIdentityProvider.get()
    had_primary_source = PrimarySourceID("00000000000000")
    identifier_in_primary_source = "thing-1"

    # assign this identity first
    identity = provider.assign(had_primary_source, identifier_in_primary_source)

    # fetch the identity we just assigned by stableTargetId
    identities = provider.fetch(
        stable_target_id=identity.stableTargetId,
    )

    # we get a perfect match
    assert identities == [identity]

    # fetch our identity with identifierInPrimarySource and hadPrimarySource
    identities = provider.fetch(
        had_primary_source=identity.hadPrimarySource,
        identifier_in_primary_source=identity.identifierInPrimarySource,
    )

    # we get a match again
    assert identities == [identity]
