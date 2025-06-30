import hashlib

from mex.common.identity.base import BaseProvider
from mex.common.identity.models import Identity
from mex.common.models import (
    MEX_PRIMARY_SOURCE_IDENTIFIER,
    MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE,
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
)
from mex.common.types import (
    AnyMergedIdentifier,
    Identifier,
    MergedPrimarySourceIdentifier,
)


class MemoryIdentityProvider(BaseProvider):
    """Connector class to handle read/write to the identity database."""

    def __init__(self) -> None:
        """Initialize an in-memory database with the identity of MEx itself."""
        self._database: list[Identity] = [
            Identity(
                identifier=MEX_PRIMARY_SOURCE_IDENTIFIER,
                hadPrimarySource=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
                identifierInPrimarySource=MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE,
                stableTargetId=MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
            )
        ]

    @staticmethod
    def _get_identifier(*args: str) -> Identifier:
        """Get deterministic identifier based on args.

        Creates a deterministic identifier by joining the arguments with newlines,
        computing an MD5 hash, and using the resulting integer as a seed for
        identifier generation.

        Args:
            *args: String arguments to use for identifier generation.

        Returns:
            Deterministic Identifier based on the input arguments.
        """
        seed_string = "\n".join(args)
        hash_ = hashlib.md5(  # noqa: S324 identifier generation is not security related
            seed_string.encode()
        )
        seed_hex = hash_.hexdigest()
        seed_int = int(seed_hex, 16)
        return Identifier.generate(seed=seed_int)

    def assign(
        self,
        had_primary_source: MergedPrimarySourceIdentifier,
        identifier_in_primary_source: str,
    ) -> Identity:
        """Find an Identity in the in-memory database or assign a new one.

        Args:
            had_primary_source: Stable target ID of primary source
            identifier_in_primary_source: Identifier in the primary source

        Returns:
            Newly created or updated Identity instance
        """
        identities = self.fetch(
            had_primary_source=had_primary_source,
            identifier_in_primary_source=identifier_in_primary_source,
        )
        if identities:
            return identities[0]

        identity = Identity(
            hadPrimarySource=had_primary_source,
            identifierInPrimarySource=identifier_in_primary_source,
            stableTargetId=self._get_identifier(
                "stableTargetId", had_primary_source, identifier_in_primary_source
            ),
            identifier=self._get_identifier(
                "identifier", had_primary_source, identifier_in_primary_source
            ),
        )
        self._database.append(identity)
        return identity

    def fetch(
        self,
        *,
        had_primary_source: MergedPrimarySourceIdentifier | None = None,
        identifier_in_primary_source: str | None = None,
        stable_target_id: AnyMergedIdentifier | None = None,
    ) -> list[Identity]:
        """Find Identity instances in the in-memory database.

        Args:
            had_primary_source: Stable target ID of primary source
            identifier_in_primary_source: Identifier in the primary source
            stable_target_id: Stable target ID of the entity

        Returns:
            List of Identity instances
        """
        identities = iter(self._database)

        if had_primary_source:
            identities = filter(
                lambda i: i.hadPrimarySource == had_primary_source, identities
            )
        if identifier_in_primary_source:
            identities = filter(
                lambda i: i.identifierInPrimarySource == identifier_in_primary_source,
                identities,
            )
        if stable_target_id:
            identities = filter(
                lambda i: i.stableTargetId == stable_target_id, identities
            )

        return list(identities)

    def metrics(self) -> dict[str, int]:
        """Generate metrics about identity provider usage."""
        return {"database_size": len(self._database)}

    def close(self) -> None:
        """Trash the in-memory identity database."""
        self._database.clear()
