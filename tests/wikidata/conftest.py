from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests
from pytest import MonkeyPatch

from mex.common.settings import BaseSettings
from mex.common.wikidata.connector import WikidataAPIConnector

TESTDATA_DIR = Path(__file__).parent / "test_data"


@pytest.fixture
def mocked_session_wikidata_api(monkeypatch: MonkeyPatch) -> MagicMock:
    """Mock and return WikidataAPIConnector with a MagicMock session."""
    mocked_session = MagicMock(spec=requests.Session)

    def __init__(self: WikidataAPIConnector) -> None:
        self.session = mocked_session

    monkeypatch.setattr(WikidataAPIConnector, "__init__", __init__)
    return mocked_session


@pytest.fixture(autouse=True)
def set_wiki_api_url_for_integration_tests(
    monkeypatch: MonkeyPatch,
    is_integration_test: bool,  # noqa: FBT001
) -> None:
    """Set correct Wikidata API URL for integration tests."""
    if is_integration_test:
        settings = BaseSettings.get()
        monkeypatch.setattr(
            settings,
            "wiki_api_url",
            "https://www.wikidata.org/w/api.php",
        )
