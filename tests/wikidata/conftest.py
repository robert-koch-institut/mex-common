from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests
from pytest import MonkeyPatch

from mex.common.wikidata.connector import (
    WikidataAPIConnector,
    WikidataQueryServiceConnector,
)

TESTDATA_DIR = Path(__file__).parent / "test_data"


@pytest.fixture
def mocked_session_wikidata_query_service(monkeypatch: MonkeyPatch) -> MagicMock:
    """Mock and return WikidataQueryServiceConnector with a MagicMock session."""
    mocked_session = MagicMock(spec=requests.Session)

    def __init__(self: WikidataQueryServiceConnector) -> None:
        self.session = mocked_session

    monkeypatch.setattr(WikidataQueryServiceConnector, "__init__", __init__)
    return mocked_session


@pytest.fixture
def mocked_session_wikidata_api(monkeypatch: MonkeyPatch) -> MagicMock:
    """Mock and return WikidataAPIConnector with a MagicMock session."""
    mocked_session = MagicMock(spec=requests.Session)

    def __init__(self: WikidataAPIConnector) -> None:
        self.session = mocked_session

    monkeypatch.setattr(WikidataAPIConnector, "__init__", __init__)
    return mocked_session
