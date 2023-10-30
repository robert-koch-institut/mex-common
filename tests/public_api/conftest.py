from unittest.mock import MagicMock, Mock

import pytest
import requests
from pytest import MonkeyPatch

from mex.common.public_api.connector import PublicApiConnector
from mex.common.public_api.models import PublicApiMetadataItemsResponse


@pytest.fixture
def mocked_api_session(monkeypatch: MonkeyPatch) -> MagicMock:
    """Mock the PublicApiConnector with a MagicMock session and return that."""
    mocked_session = MagicMock(spec=requests.Session, name="public_api_session")
    mocked_session.request = MagicMock(
        return_value=Mock(spec=requests.Response, status_code=200)
    )

    def set_mocked_session(self: PublicApiConnector) -> None:
        self.session = mocked_session

    monkeypatch.setattr(PublicApiConnector, "_set_session", set_mocked_session)
    monkeypatch.setattr(PublicApiConnector, "wait_for_job", MagicMock())
    return mocked_session


@pytest.fixture
def mocked_api_session_authenticated(mocked_api_session: MagicMock) -> MagicMock:
    """Get the authenticated MagicMock session."""
    mocked_api_session.post = mocked_post = MagicMock(
        return_value=Mock(spec=requests.Response),
    )
    mocked_api_session.headers = {}
    mocked_post.return_value.json = MagicMock(
        return_value={
            "access_token": "expected-jwt",
            "expires_in": 300,
            "token_type": "Bearer",
        },
    )
    return mocked_api_session


@pytest.fixture
def mex_metadata_items_response() -> PublicApiMetadataItemsResponse:
    """Return a dummy PublicApiMetadataItemsResponse for testing purposes."""
    return PublicApiMetadataItemsResponse.model_validate(
        {
            "items": [
                {
                    "itemId": "00005da9-f653-4c9c-b123-7b555d36b0fd",
                    "businessId": "bgmAz9QJ7IaHGNyMamwhUx",
                    "entityType": "Datum",
                },
                {
                    "itemId": "000054a2-b16a-4f4e-82d2-1a222dba41e6",
                    "businessId": "hLRKpjTpCS06BniW1l2NcU",
                    "entityType": "ExtractedDatum",
                },
                {
                    "itemId": "000054a2-b16a-4f4e-82d2-1a222fba41e6",
                    "businessId": "g5MAfZYmivhK1I2voBK5bO",
                    "entityType": "ExtractedPerson",
                },
                {
                    "itemId": "000054a3-b16a-4f4e-82d2-1a222fbc41e6",
                    "businessId": "cOfkBGYSeIjcKCdDZJQ0yk",
                    "entityType": "Person",
                },
            ],
            "next": "",
        }
    )
