from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests
from pytest import MonkeyPatch

from mex.common.models.primary_source import ExtractedPrimarySource
from mex.common.primary_source.extract import extract_mex_db_primary_source_by_id
from mex.common.primary_source.transform import (
    transform_mex_db_primary_source_to_extracted_primary_source,
)
from mex.common.settings import BaseSettings
from mex.common.testing import insert_test_primary_sources_into_db
from mex.common.wikidata.connector import (
    WikidataAPIConnector,
    WikidataQueryServiceConnector,
)

TESTDATA_DIR = Path(__file__).parent / "test_data"


@pytest.fixture(autouse=True)
def seed_primary_sources_into_db() -> None:
    """Seed wikidata and mex-db primary sources data into temp database."""
    insert_test_primary_sources_into_db("mex-db", "ldap", "wikidata")


@pytest.fixture
@pytest.mark.usefixtures("seed_primary_sources_into_db")
def wikidata_primary_source() -> ExtractedPrimarySource:
    """Return a dummy wikidata primary source to use for testing."""
    mex_db_primary_source = extract_mex_db_primary_source_by_id("wikidata")
    return transform_mex_db_primary_source_to_extracted_primary_source(
        mex_db_primary_source
    )


@pytest.fixture
def mocked_session_wikidata_query_service(monkeypatch: MonkeyPatch) -> MagicMock:
    """Mock and return WikidataQueryServiceConnector with a MagicMock session."""
    mocked_session = MagicMock(spec=requests.Session)

    def mocked_init(
        self: WikidataQueryServiceConnector, settings: BaseSettings
    ) -> None:
        self.session = mocked_session

    monkeypatch.setattr(WikidataQueryServiceConnector, "__init__", mocked_init)

    return mocked_session


@pytest.fixture
def mocked_session_wikidata_api(monkeypatch: MonkeyPatch) -> MagicMock:
    """Mock and return WikidataAPIConnector with a MagicMock session."""
    mocked_session = MagicMock(spec=requests.Session)

    def mocked_init(self: WikidataAPIConnector, settings: BaseSettings) -> None:
        self.session = mocked_session

    monkeypatch.setattr(WikidataAPIConnector, "__init__", mocked_init)
    return mocked_session
