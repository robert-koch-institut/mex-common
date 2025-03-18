from functools import cache

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.identity.base import BaseProvider
from mex.common.identity.models import Identity
from mex.common.models import ItemsContainer
from mex.common.types import Identifier, MergedPrimarySourceIdentifier


class BackendApiIdentityProvider(BaseProvider, BackendApiConnector):
    """Identity provider that communicates with the backend HTTP API."""

    @cache  # noqa: B019
    def assign(
        self,
        had_primary_source: MergedPrimarySourceIdentifier,
        identifier_in_primary_source: str,
    ) -> Identity:
        """Find an Identity in a database or assign a new one."""
        response = self.request(
            "POST",
            "identity",
            {
                "hadPrimarySource": had_primary_source,
                "identifierInPrimarySource": identifier_in_primary_source,
            },
        )
        return Identity.model_validate(response)

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
        response = self.request(
            "GET",
            "identity",
            params={
                "hadPrimarySource": had_primary_source,
                "identifierInPrimarySource": identifier_in_primary_source,
                "stableTargetId": stable_target_id,
            },
        )
        return ItemsContainer[Identity].model_validate(response).items
