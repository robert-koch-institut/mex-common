from functools import lru_cache

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.identity.base import BaseProvider
from mex.common.identity.models import Identity
from mex.common.types import Identifier, MergedPrimarySourceIdentifier

IDENTITY_CACHE_SIZE = 5000


class BackendApiIdentityProvider(BaseProvider):
    """Identity provider that communicates with the backend HTTP API."""

    def __init__(self) -> None:
        """Create a new backend identity provider."""
        # mitigating https://docs.astral.sh/ruff/rules/cached-instance-method
        self._cached_assign = lru_cache(IDENTITY_CACHE_SIZE)(self._do_assign)

    def assign(
        self,
        had_primary_source: MergedPrimarySourceIdentifier,
        identifier_in_primary_source: str,
    ) -> Identity:
        """Return a cached Identity from the backend."""
        return self._cached_assign(had_primary_source, identifier_in_primary_source)

    def _do_assign(
        self,
        had_primary_source: MergedPrimarySourceIdentifier,
        identifier_in_primary_source: str,
    ) -> Identity:
        """Find an Identity in the backend or let the backend assign a new one."""
        connector = BackendApiConnector.get()
        return connector.assign_identity(
            had_primary_source=had_primary_source,
            identifier_in_primary_source=identifier_in_primary_source,
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
        connector = BackendApiConnector.get()
        response = connector.fetch_identities(
            had_primary_source=had_primary_source,
            identifier_in_primary_source=identifier_in_primary_source,
            stable_target_id=stable_target_id,
        )
        return response.items

    def metrics(self) -> dict[str, int]:
        """Generate metrics about identity provider usage."""
        cache_info = self._cached_assign.cache_info()
        return {"cache_hits": cache_info.hits, "cache_misses": cache_info.misses}

    def close(self) -> None:
        """Clear the connector cache."""
        self._cached_assign.cache_clear()
