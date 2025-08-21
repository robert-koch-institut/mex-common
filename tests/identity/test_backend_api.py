from unittest.mock import MagicMock, Mock

import pytest
import requests
from pytest import MonkeyPatch

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.identity import Identity
from mex.common.identity.backend_api import BackendApiIdentityProvider
from mex.common.models import ExtractedContactPoint
from mex.common.types import MergedPrimarySourceIdentifier


@pytest.fixture
def mocked_backend_connector(monkeypatch: MonkeyPatch) -> MagicMock:
    mocked_session = MagicMock(spec=requests.Session)
    mocked_session.request = MagicMock(
        return_value=Mock(spec=requests.Response, status_code=200)
    )
    mocked_session.headers = {}

    def set_mocked_session(self: BackendApiConnector) -> None:
        self.session = mocked_session

    monkeypatch.setattr(BackendApiConnector, "_set_session", set_mocked_session)
    return mocked_session


def test_assign_mocked(
    mocked_backend_connector: requests.Session,
) -> None:
    mocked_data = {
        "identifier": MergedPrimarySourceIdentifier.generate(seed=962),
        "hadPrimarySource": MergedPrimarySourceIdentifier.generate(seed=961),
        "identifierInPrimarySource": "test",
        "stableTargetId": MergedPrimarySourceIdentifier.generate(seed=963),
    }
    mocked_response = Mock(spec=requests.Response)
    mocked_response.status_code = 200
    mocked_response.json = MagicMock(return_value=mocked_data)
    mocked_backend_connector.request = MagicMock(return_value=mocked_response)  # type: ignore[method-assign]

    provider = BackendApiIdentityProvider.get()
    identity_first = provider.assign(
        had_primary_source=MergedPrimarySourceIdentifier.generate(seed=961),
        identifier_in_primary_source="test",
    )

    identity = Identity.model_validate(identity_first)

    identity_first_assignment = identity.model_dump()

    assert identity_first_assignment == mocked_data

    identity_second = provider.assign(
        had_primary_source=MergedPrimarySourceIdentifier.generate(seed=961),
        identifier_in_primary_source="test",
    )
    identity_second_assignment = identity_second.model_dump()

    assert identity_second_assignment == identity_first_assignment


def test_fetch_mocked(
    mocked_backend_connector: requests.Session,
) -> None:
    mocked_data = {
        "items": [
            {
                "identifier": MergedPrimarySourceIdentifier.generate(seed=962),
                "hadPrimarySource": MergedPrimarySourceIdentifier.generate(seed=961),
                "identifierInPrimarySource": "test",
                "stableTargetId": MergedPrimarySourceIdentifier.generate(seed=963),
            }
        ],
        "total": 1,
    }

    mocked_response = Mock(spec=requests.Response)
    mocked_response.status_code = 200
    mocked_response.json = MagicMock(return_value=mocked_data)
    mocked_backend_connector.request = MagicMock(return_value=mocked_response)  # type: ignore[method-assign]

    provider = BackendApiIdentityProvider.get()

    contact_point = ExtractedContactPoint(
        hadPrimarySource=MergedPrimarySourceIdentifier.generate(seed=961),
        identifierInPrimarySource="test",
        email=["test@test.de"],
    )

    identities = provider.fetch(stable_target_id=contact_point.stableTargetId)
    assert identities == [
        Identity(
            stableTargetId=mocked_data["items"][0]["stableTargetId"],  # type: ignore[index]
            identifier=mocked_data["items"][0]["identifier"],  # type: ignore[index]
            hadPrimarySource=contact_point.hadPrimarySource,
            identifierInPrimarySource=contact_point.identifierInPrimarySource,
        )
    ]

    identities = provider.fetch(
        had_primary_source=contact_point.hadPrimarySource,
        identifier_in_primary_source=contact_point.identifierInPrimarySource,
    )
    assert identities == [
        Identity(
            stableTargetId=mocked_data["items"][0]["stableTargetId"],  # type: ignore[index]
            identifier=mocked_data["items"][0]["identifier"],  # type: ignore[index]
            hadPrimarySource=contact_point.hadPrimarySource,
            identifierInPrimarySource=contact_point.identifierInPrimarySource,
        )
    ]


def test_fetch_mocked_empty(
    mocked_backend_connector: requests.Session,
) -> None:
    mocked_response = Mock(spec=requests.Response)
    mocked_response.status_code = 200
    mocked_response.json = MagicMock(return_value={"items": [], "total": 0})
    mocked_backend_connector.request = MagicMock(return_value=mocked_response)  # type: ignore[method-assign]

    provider = BackendApiIdentityProvider.get()

    provider.fetch()

    mocked_backend_connector.request.assert_called_with(
        "GET",
        "http://localhost:8080/v0/identity",
        {
            "hadPrimarySource": None,
            "identifierInPrimarySource": None,
            "stableTargetId": None,
        },
        timeout=10,
        headers={"Accept": "application/json", "User-Agent": "rki/mex"},
    )
