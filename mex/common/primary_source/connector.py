from typing import List, Optional

from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import sessionmaker

from mex.common.db.connector import MexDBConnector
from mex.common.exceptions import EmptySearchResultError
from mex.common.primary_source.models import (
    AlternativeTitle,
    Contact,
    Description,
    Documentation,
    LocatedAt,
    MExDBPrimarySource,
    Title,
    UnitInCharge,
)


class MExDBPrimarySourceConnector(MexDBConnector):
    """Handle database operations for mex primary sources."""

    def upsert(
        self,
        identifier: str,
        alternative_titles: list[str],
        contacts: list[str],
        descriptions: list[str],
        documentations: list[str],
        located_ats: list[str],
        titles: list[str],
        units_in_charge: list[str],
        version: Optional[str],
    ) -> None:
        """Insert/update database enteries for mex primary source and all dependent relations.

        Args:
            identifier: Identifier of the primary source
            alternative_titles: Alternative titles of the primary source
            contacts: Contacts assosiated with the primary source
            descriptions: Description of the primary source
            documentations: Documentations of the primary source
            located_ats: Located at info of the primary source
            titles: Titles of the primary source
            units_in_charge: Units in charge of the primary source
            version: Version of the primary source
        """
        created_primary_source = self.engine.execute(
            insert(MExDBPrimarySource).values(identifier=identifier, version=version)
        )

        for alternative_title in alternative_titles:
            self.engine.execute(
                insert(AlternativeTitle).values(
                    alternative_title=alternative_title,
                    primary_source_id=created_primary_source.inserted_primary_key[0],
                )
            )
        for contact in contacts:
            self.engine.execute(
                insert(Contact).values(
                    contact=contact,
                    primary_source_id=created_primary_source.inserted_primary_key[0],
                )
            )
        for description in descriptions:
            self.engine.execute(
                insert(Description).values(
                    description=description,
                    primary_source_id=created_primary_source.inserted_primary_key[0],
                )
            )
        for documentation in documentations:
            self.engine.execute(
                insert(Documentation).values(
                    documentation=documentation,
                    primary_source_id=created_primary_source.inserted_primary_key[0],
                )
            )

        for located_at in located_ats:
            self.engine.execute(
                insert(LocatedAt).values(
                    located_at=located_at,
                    primary_source_id=created_primary_source.inserted_primary_key[0],
                )
            )

        for title in titles:
            self.engine.execute(
                insert(Title).values(
                    title=title,
                    primary_source_id=created_primary_source.inserted_primary_key[0],
                )
            )
        for unit_in_charge in units_in_charge:
            self.engine.execute(
                insert(UnitInCharge).values(
                    unit_in_charge=unit_in_charge,
                    primary_source_id=created_primary_source.inserted_primary_key[0],
                )
            )

    def fetch_all_primary_sources(self) -> List[MExDBPrimarySource]:
        """Fetch all primary sources from database.

        Returns:
            List of primary source objects
        """
        session = sessionmaker(bind=self.engine)()

        primary_sources = session.query(MExDBPrimarySource).all()

        return primary_sources

    def fetch_one_primary_source(
        self,
        identifier_in_primary_source: str,
    ) -> MExDBPrimarySource:
        """Fetch one primary source by its readable identifier.

        Args:
            identifier_in_primary_source: Identifier of the primary source (e.g. rdmo, ff-projects)

        Raises:
            MExError: Raises no results found exception

        Returns:
            primary_source: primary_source object with its relations to other objects
                e.g. labels, api_type intact
        """
        session = sessionmaker(bind=self.engine, autoflush=False)()

        primary_source: Optional[MExDBPrimarySource] = (
            session.query(MExDBPrimarySource)
            .filter(MExDBPrimarySource.identifier == identifier_in_primary_source)
            .one_or_none()
        )

        if not primary_source:
            raise EmptySearchResultError(
                f"No primary_source found with identifier in primary source: '{identifier_in_primary_source}'. "
                "Did you execute 'seed-mex-db'?"
            )

        return primary_source
