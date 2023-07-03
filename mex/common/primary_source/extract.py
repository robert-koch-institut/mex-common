from mex.common.primary_source.connector import MExDBPrimarySourceConnector
from mex.common.primary_source.models import MExDBPrimarySource, SeedPrimarySource


def insert_primary_source_into_db(primary_source: SeedPrimarySource) -> None:
    """Insert single primary source data into database.

    Args:
        primary_source: primary source data model
    """
    connector = MExDBPrimarySourceConnector.get()
    connector.upsert(
        identifier=primary_source.identifier,
        alternative_titles=primary_source.alternative_title,
        contacts=primary_source.contact,
        descriptions=primary_source.description,
        documentations=primary_source.documentation,
        located_ats=primary_source.located_at,
        titles=primary_source.title,
        units_in_charge=primary_source.unit_in_charge,
        version=primary_source.version,
    )


def extract_mex_db_primary_source_by_id(
    identifier_in_primary_source: str,
) -> MExDBPrimarySource:
    """Extract a primary_source from mex-database by human-readable id.

    Args:
        identifier_in_primary_source: Human readable id of the primary source .e.g: rdmo, ff-projects

    Returns:
        MExDBPrimarySource: MExDBPrimarySource ORM object
    """
    connector = MExDBPrimarySourceConnector.get()
    return connector.fetch_one_primary_source(identifier_in_primary_source)
