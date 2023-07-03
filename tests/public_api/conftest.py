from unittest.mock import MagicMock

import pytest
import requests
from pytest import MonkeyPatch

from mex.common.public_api.connector import PublicApiConnector
from mex.common.public_api.models import PublicApiMetadataItemsResponse
from mex.common.settings import BaseSettings


@pytest.fixture
def mocked_api_session(monkeypatch: MonkeyPatch) -> MagicMock:
    """Mock the PublicApiConnector with a MagicMock session and return that."""
    mocked_session = MagicMock(spec=requests.Session)

    def mocked_init(self: PublicApiConnector, settings: BaseSettings) -> None:
        self.session = mocked_session
        self.url = settings.public_api_url
        self.token_provider = settings.public_api_token_provider
        self.token_payload = settings.public_api_token_payload

    monkeypatch.setattr(PublicApiConnector, "__init__", mocked_init)
    monkeypatch.setattr(PublicApiConnector, "wait_for_job", MagicMock())
    return mocked_session


@pytest.fixture
def mex_metadata_items_response() -> PublicApiMetadataItemsResponse:
    """Return a dummy PublicApiMetadataItemsResponse for testing purposes."""
    return PublicApiMetadataItemsResponse.parse_obj(
        {
            "items": [
                {
                    "itemId": "00005da9-f653-4c9c-b123-7b555d36b0fd",
                    "entityType": "Datum",
                },
                {
                    "itemId": "000054a2-b16a-4f4e-82d2-1a222dba41e6",
                    "entityType": "ExtractedDatum",
                },
                {
                    "itemId": "000054a2-b16a-4f4e-82d2-1a222fba41e6",
                    "entityType": "ExtractedPerson",
                },
                {
                    "itemId": "000054a3-b16a-4f4e-82d2-1a222fbc41e6",
                    "entityType": "Person",
                },
            ],
            "next": "",
        }
    )
