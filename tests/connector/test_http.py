from typing import Any
from unittest.mock import MagicMock, Mock, call

import pytest
import requests
from pytest import MonkeyPatch
from requests import JSONDecodeError, Response

from mex.common.connector import (
    CONNECTOR_STORE,
    HTTPConnector,
)


class DummyHTTPConnector(HTTPConnector):
    def _set_url(self) -> None:
        self.url = "https://www.example.com"

    def _check_availability(self) -> None:
        self.request("GET", "_system/check")


@pytest.fixture
def mocked_dummy_session(monkeypatch: MonkeyPatch) -> MagicMock:
    """Mock the DummyHTTPConnector with a MagicMock session and return that."""
    mocked_session = MagicMock(spec=requests.Session, name="dummy_session")
    mocked_session.request = MagicMock(
        return_value=Mock(spec=requests.Response, status_code=200)
    )

    def set_mocked_session(self: DummyHTTPConnector) -> None:
        self.session = mocked_session

    monkeypatch.setattr(DummyHTTPConnector, "_set_session", set_mocked_session)
    return mocked_session


def test_init_mocked(mocked_dummy_session: MagicMock) -> None:
    connector = DummyHTTPConnector.get()
    connector.request("GET", "_system/check")
    assert connector.url == "https://www.example.com"
    assert mocked_dummy_session.request.call_args_list[-1] == call(
        "GET",
        "https://www.example.com/_system/check",
        None,
        timeout=10,
        headers={"Accept": "application/json"},
    )


@pytest.mark.usefixtures("mocked_dummy_session")
def test_reset_all_connectors(mocked_dummy_session: MagicMock) -> None:
    DummyHTTPConnector.get()
    assert len(list(CONNECTOR_STORE)) == 1

    CONNECTOR_STORE.reset()
    mocked_dummy_session.close.assert_called_once_with()

    assert len(list(CONNECTOR_STORE)) == 0


@pytest.mark.parametrize(
    ("sent_payload", "mocked_response", "expected_response", "expected_kwargs"),
    [
        (
            {},
            MagicMock(status_code=204, json=MagicMock(side_effect=JSONDecodeError)),
            {},
            {"headers": {"Accept": "application/json"}},
        ),
        (
            {},
            MagicMock(status_code=200, json=MagicMock(return_value={"foo": "bar"})),
            {"foo": "bar"},
            {"headers": {"Accept": "application/json"}},
        ),
        (
            {"q": "SELECT status;"},
            MagicMock(status_code=200, json=MagicMock(return_value={"status": 42})),
            {"status": 42},
            {
                "headers": {
                    "Accept": "application/json",
                    "User-Agent": "rki/mex",
                },
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
    sent_payload: dict[str, Any] | None,
    mocked_response: Response,
    expected_response: dict[str, Any],
    expected_kwargs: dict[str, Any],
) -> None:
    mocked_session = MagicMock(spec=requests.Session, name="dummy_session")
    mocked_session.request = MagicMock(return_value=mocked_response)

    def set_mocked_session(self: DummyHTTPConnector) -> None:
        self.session = mocked_session

    monkeypatch.setattr(DummyHTTPConnector, "_set_session", set_mocked_session)

    connector = DummyHTTPConnector.get()

    actual_response = connector.request("POST", "things", payload=sent_payload)

    assert actual_response == expected_response
    assert mocked_session.request.call_args_list[-1] == call(
        "POST",
        "https://www.example.com/things",
        None,
        timeout=DummyHTTPConnector.TIMEOUT,
        **expected_kwargs,
    )
