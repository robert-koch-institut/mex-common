from typing import Iterable, Optional

from mex.common.connector import BaseConnector
from mex.common.identity.models import Identity
from mex.common.settings import BaseSettings
from mex.common.types import Identifier


class IdentityConnector(BaseConnector):
    """Connector class to handle read/write to the identity database."""

    def __init__(self, settings: BaseSettings) -> None:
        """Initialize a dummy identity database as a list of identity instances."""
        self.dummy_identity_db: list[Identity] = []

    def upsert(
        self,
        had_primary_source: Identifier,
        identifier_in_primary_source: str,
        stable_target_id: Identifier,
        entity_type: str,
    ) -> Identity:
        """Insert a new identity or update an existing one.

        Args:
            had_primary_source: Stable target ID of primary source
            identifier_in_primary_source: Identifier in the primary source
            stable_target_id: Stable target ID of the entity
            entity_type: Type of the entity

        Returns:
            Newly created or updated Identity instance
        """
        identity = self.fetch(
            had_primary_source=had_primary_source,
            identifier_in_primary_source=identifier_in_primary_source,
        )
        if identity:
            identity.stableTargetId = stable_target_id
        else:
            identity = Identity(
                hadPrimarySource=had_primary_source,
                identifierInPrimarySource=identifier_in_primary_source,
                stableTargetId=stable_target_id,
                entityType=entity_type,
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
    ) -> Optional[Identity]:
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
