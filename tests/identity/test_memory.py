from mex.common.identity.memory import MemoryIdentityProvider
from mex.common.testing import Joker
from mex.common.types import MergedPrimarySourceIdentifier


def test_get_identifier() -> None:
    assert MemoryIdentityProvider._get_identifier(
        "foo"
    ) == MemoryIdentityProvider._get_identifier("foo")
    assert MemoryIdentityProvider._get_identifier(
        "foo"
    ) != MemoryIdentityProvider._get_identifier("bar")
    identifiers = [
        MemoryIdentityProvider._get_identifier(arg1, arg2)
        for arg1 in ["foo", "bar"]
        for arg2 in ["a", "b", "c"]
    ]
    # make sure each combination of args results in a unique identifier
    assert len(set(identifiers)) == len(identifiers)


def test_assign() -> None:
    provider = MemoryIdentityProvider.get()
    had_primary_source = MergedPrimarySourceIdentifier("00000000000000")
    identifier_in_primary_source = "thing-1"

    new_identity = provider.assign(had_primary_source, identifier_in_primary_source)

    assert new_identity.model_dump() == {
        "hadPrimarySource": had_primary_source,
        "identifierInPrimarySource": identifier_in_primary_source,
        "stableTargetId": Joker(),
        "identifier": Joker(),
    }

    found_identity = provider.assign(had_primary_source, identifier_in_primary_source)

    assert found_identity.model_dump() == {
        "hadPrimarySource": had_primary_source,
        "identifierInPrimarySource": identifier_in_primary_source,
        "stableTargetId": new_identity.stableTargetId,
        "identifier": new_identity.identifier,
    }

    provider.close()
    provider = MemoryIdentityProvider.get()
    fresh_identity = provider.assign(had_primary_source, identifier_in_primary_source)

    assert fresh_identity.model_dump() == {
        "hadPrimarySource": had_primary_source,
        "identifierInPrimarySource": identifier_in_primary_source,
        "stableTargetId": new_identity.stableTargetId,
        "identifier": new_identity.identifier,
    }


def test_fetch_empty() -> None:
    provider = MemoryIdentityProvider.get()
    had_primary_source = MergedPrimarySourceIdentifier("00000000000000")
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
    had_primary_source = MergedPrimarySourceIdentifier("00000000000000")
    identifier_in_primary_source = "thing-1"

    # assign this identity first
    identity = provider.assign(had_primary_source, identifier_in_primary_source)

    # fetch the identity we just assigned by stableTargetId
    identities = provider.fetch(
        stable_target_id=identity.stableTargetId,  # type: ignore[arg-type]
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
