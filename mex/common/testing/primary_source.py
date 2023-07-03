from mex.common.primary_source.extract import insert_primary_source_into_db
from mex.common.primary_source.models import SeedPrimarySource


def insert_test_primary_sources_into_db(*primary_source_ids: str) -> None:
    """Seed primary sources for the given identifiers into the test database."""
    for primary_source_id in primary_source_ids:
        primary_source = SeedPrimarySource(
            identifier=primary_source_id,
            alternative_title=['{"value": "PM"}'],
            contact=["00000000-0000-4000-8000-00000aaeeddd"],
            description=['{"language": "de", "value": "Probenmaterial Description"}'],
            documentation=[
                '{"language": "de", "title": "Probenmaterial Docs", "url": "https://probenmaterial.test/docs"}',
                '{"language": "en", "title": "Probenmaterial Docs Eng", "url": "https://probenmaterial.test/docs_en"}',
            ],
            located_at=[
                '{"language": "de", "title": "Probenmaterial", "url": "https://probenmaterial.test"}',
                '{"language": "en", "title": "Test Material", "url": "https://probenmaterial.test/en"}',
            ],
            title=['{"language": "de", "value": "Probenmaterial"}'],
            unit_in_charge=["PRNT"],
            version="1.29",
        )
        insert_primary_source_into_db(primary_source)
