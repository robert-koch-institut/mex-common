from mex.common.backend_api.helpers import assign_identity, fetch_identities
from mex.common.identity.base import BaseProvider
from mex.common.identity.models import Identity
from mex.common.types import Identifier, MergedPrimarySourceIdentifier


class BackendApiIdentityProvider(BaseProvider):
    """Identity provider that communicates with the backend HTTP API."""

    def __init__(self) -> None:
        """Create a new connector instance."""

    def assign(
        self,
        had_primary_source: MergedPrimarySourceIdentifier,
        identifier_in_primary_source: str,
    ) -> Identity:
        """Find an Identity in a database or assign a new one."""
        return assign_identity(
            had_primary_source,
            identifier_in_primary_source,
        )

    def fetch(
        self,
        *,
        had_primary_source: Identifier | None = None,
        identifier_in_primary_source: str | None = None,
        stable_target_id: Identifier | None = None,
    ) -> list[Identity]:
        """Find Identity instances matching the given filters.

        Either provide `stableTargetId` or `hadPrimarySource`
        and `identifierInPrimarySource` together to get a unique result.
        """
        return fetch_identities(
            had_primary_source=had_primary_source,
            identifier_in_primary_source=identifier_in_primary_source,
            stable_target_id=stable_target_id,
        )

    def close(self) -> None:
        """Nothing to close because of delegation to backend api connector."""
