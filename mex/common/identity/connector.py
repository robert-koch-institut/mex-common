from typing import Optional, cast

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert

from mex.common.db.connector import MexDBConnector
from mex.common.identity.models import Identity
from mex.common.types import Identifier


class IdentityConnector(MexDBConnector):
    """Connector class to handle read/write to the identity database."""

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
        self.engine.execute(
            insert(Identity)
            .values(
                fragment_id=str(Identifier.generate()),
                platform_id=str(had_primary_source),
                original_id=identifier_in_primary_source,
                merged_id=str(stable_target_id),
                entity_type=entity_type,
                annotation="-",  # deprecated
            )
            .on_conflict_do_update(
                ["platform_id", "original_id"],
                set_={"merged_id": str(stable_target_id)},
            )
        )
        return cast(
            Identity,
            self.fetch(
                had_primary_source=had_primary_source,
                identifier_in_primary_source=identifier_in_primary_source,
            ),
        )

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
        query = select(Identity)
        if had_primary_source:
            query = query.where(Identity.platform_id == str(had_primary_source))
        if identifier_in_primary_source:
            query = query.where(
                Identity.original_id == str(identifier_in_primary_source)
            )
        if stable_target_id:
            query = query.where(Identity.merged_id == str(stable_target_id))
        cursor = self.engine.execute(query)
        return cast(Optional[Identity], cursor.fetchone())
