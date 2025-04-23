from functools import lru_cache

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.identity.models import Identity
from mex.common.types import Identifier, MergedPrimarySourceIdentifier


@lru_cache(maxsize=1024)
def assign_identity(
    had_primary_source: MergedPrimarySourceIdentifier,
    identifier_in_primary_source: str,
) -> Identity:
    """Find an Identity in a database or assign a new one."""
    connector = BackendApiConnector.get()
    return connector.assign_identity(
        had_primary_source=had_primary_source,
        identifier_in_primary_source=identifier_in_primary_source,
    )


def fetch_identities(
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
