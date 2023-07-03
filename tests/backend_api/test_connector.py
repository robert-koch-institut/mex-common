import json
from typing import Any, Optional
from unittest.mock import MagicMock, Mock, call

import pytest
from pytest import MonkeyPatch
from requests import JSONDecodeError, Response
from requests.exceptions import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models.person import ExtractedPerson
from mex.common.testing import Joker


def test_init_mocked(monkeypatch: MonkeyPatch) -> None:
    mocked_request = MagicMock()
    monkeypatch.setattr(BackendApiConnector, "request", mocked_request)
    connector = BackendApiConnector.get()

    mocked_request.assert_called_once_with("GET", "_system/check")
    assert connector.session.headers["Accept"] == "application/json"
    assert connector.session.headers["User-Agent"] == "rki/mex"
    assert connector.url == "http://localhost:8080/"


@pytest.mark.parametrize(
    "sent_payload, mocked_response, expected_response, expected_kwargs",
    [
        (
            {},
            MagicMock(status_code=204, json=MagicMock(side_effect=JSONDecodeError)),
            {},
            {},
        ),
        (
            {},
            MagicMock(status_code=200, json=MagicMock(return_value={"foo": "bar"})),
            {"foo": "bar"},
            {},
        ),
        (
            {"q": "SELECT status;"},
            MagicMock(status_code=200, json=MagicMock(return_value={"status": 42})),
            {"status": 42},
            {
                "headers": {"Content-Type": "application/json"},
                "data": '{"q": "SELECT status;"}',
            },
        ),
    ],
    ids=[
        "sending no payload and receiving 204 response",
        "sending no payload and receiving 200 response",
        "sending payload and receiving 200 response",
    ],
)
def test_request_success(
    monkeypatch: MonkeyPatch,
    sent_payload: Optional[dict[str, Any]],
    mocked_response: Response,
    expected_response: dict[str, Any],
    expected_kwargs: dict[str, Any],
) -> None:
    mocked_send_request = MagicMock(
        name="_send_request",
        spec=BackendApiConnector._send_request,
        return_value=mocked_response,
    )
    monkeypatch.setattr(BackendApiConnector, "_send_request", mocked_send_request)

    connector = BackendApiConnector.get()

    actual_response = connector.request("POST", "things", payload=sent_payload)
    assert actual_response == expected_response
    assert mocked_send_request.call_args_list[-1] == call(
        "POST",
        "http://localhost:8080/v0/things",
        timeout=BackendApiConnector.TIMEOUT,
        **expected_kwargs
    )


def test_request_error_mocked(monkeypatch: MonkeyPatch) -> None:
    mocked_response = MagicMock(
        raise_for_status=MagicMock(side_effect=HTTPError("Ooops"))
    )
    mocked_send_request = MagicMock(
        spec=BackendApiConnector._send_request,
        side_effect=[Mock(), mocked_response],
        json=dict,
    )
    monkeypatch.setattr(BackendApiConnector, "_send_request", mocked_send_request)

    connector = BackendApiConnector.get()
    with pytest.raises(HTTPError, match="Ooops"):
        connector.request("GET", "fail")


def test_post_models(
    monkeypatch: MonkeyPatch, extracted_person: ExtractedPerson
) -> None:
    mocked_send_request = MagicMock(
        spec=BackendApiConnector._send_request,
        return_value=Mock(json=MagicMock(return_value={"identifiers": []})),
    )
    monkeypatch.setattr(BackendApiConnector, "_send_request", mocked_send_request)

    connector = BackendApiConnector.get()
    connector.post_models([extracted_person])

    assert mocked_send_request.call_args_list[-1] == call(
        "POST",
        "http://localhost:8080/v0/entity",
        timeout=BackendApiConnector.TIMEOUT,
        headers={"Content-Type": "application/json"},
        data=Joker(),
    )

    assert json.loads(mocked_send_request.call_args_list[-1].kwargs["data"]) == {
        "ExtractedPerson": [
            {
                "affiliation": ["bFQoRhcVH5DHZg"],
                "email": "TintzmannM@rki.de",
                "familyName": ["Tintzmann"],
                "fullName": ["Meinrad I. Tintzmann"],
                "givenName": ["Meinrad"],
                "hadPrimarySource": "bFQoRhcVH5DHXE",
                "identifier": "bFQoRhcVH5DH3i",
                "identifierInPrimarySource": "00000000-0000-4000-8000-0000000003de",
                "isniId": "https://isni.org/isni/0000000109403744",
                "memberOf": ["bFQoRhcVH5DHV2", "bFQoRhcVH5DHV3"],
                "orcidId": "https://orcid.org/0000-0002-9079-593X",
                "stableTargetId": "bFQoRhcVH5DH8y",
            }
        ]
    }
