from unittest.mock import MagicMock, Mock

import pytest
import requests
from pytest import MonkeyPatch

from mex.common.connector import HTTPConnector
from mex.common.settings import BaseSettings


@pytest.fixture
def mocked_api_session(monkeypatch: MonkeyPatch) -> MagicMock:
    """Mock the PublicApiConnector with a MagicMock session and return that."""
    mocked_session = MagicMock(spec=requests.Session, name="dummy_session")
    mocked_session.request = MagicMock(
        return_value=Mock(spec=requests.Response, status_code=200)
    )

    def set_mocked_session(self: HTTPConnector, settings: BaseSettings) -> None:
        self.session = mocked_session

    monkeypatch.setattr(HTTPConnector, "_set_session", set_mocked_session)
    monkeypatch.setattr(HTTPConnector, "wait_for_job", MagicMock())
    return mocked_session
