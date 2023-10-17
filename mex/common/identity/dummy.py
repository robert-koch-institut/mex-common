from typing import Iterable

from mex.common.connector import BaseConnector
from mex.common.identity.base import BaseProvider
from mex.common.identity.models import Identity
from mex.common.settings import BaseSettings
from mex.common.types import Identifier, PrimarySourceID


class DummyIdentityProvider(BaseProvider, BaseConnector):
    """Connector class to handle read/write to the identity database."""

    def __init__(self, settings: BaseSettings) -> None:
        """Initialize a dummy identity database as a list of identity instances."""
        self.dummy_identity_db: list[Identity] = []

    def assign(
        self, had_primary_source: PrimarySourceID, identifier_in_primary_source: str
    ) -> Identity:
        """Find an Identity or assign a new one.

        Args:
            had_primary_source: Stable target ID of primary source
            identifier_in_primary_source: Identifier in the primary source

        Returns:
            Newly created or updated Identity instance
        """
        identity = self.fetch(
            had_primary_source=had_primary_source,
            identifier_in_primary_source=identifier_in_primary_source,
        )
        if not identity:
            identity = Identity(
                hadPrimarySource=had_primary_source,
                identifierInPrimarySource=identifier_in_primary_source,
                stableTargetId=Identifier.generate(),
                identifier=Identifier.generate(),
            )
            self.dummy_identity_db.append(identity)
        return identity

    def fetch(
        self,
        *,
        had_primary_source: Identifier | None = None,
        identifier_in_primary_source: str | None = None,
        stable_target_id: Identifier | None = None,
    ) -> Identity | None:
        """Find an Identity instance from the database if it can be found.

        Args:
            had_primary_source: Stable target ID of primary source
            identifier_in_primary_source: Identifier in the primary source
            stable_target_id: Stable target ID of the entity

        Returns:
            Optional Identity instance
        """
        identities: Iterable[Identity] = self.dummy_identity_db

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

        if identities := list(identities):
            return identities[0]
        return None

    def close(self) -> None:
        """Trash the dummy identity database."""
        self.dummy_identity_db.clear()
