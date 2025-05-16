import time
from typing import Any
from unittest.mock import MagicMock, Mock, call

import pytest
import requests
from pytest import LogCaptureFixture, MonkeyPatch
from requests import ConnectTimeout, JSONDecodeError, RequestException, Response, codes

from mex.common.connector import CONNECTOR_STORE, HTTPConnector
from mex.common.exceptions import TimedReadTimeout


class DummyHTTPConnector(HTTPConnector):
    TIMEOUT = 1
    TIMEOUT_MAX = 2
    PROPORTIONAL_BACKOFF_MIN = 0.1

    def _set_url(self) -> None:
        self.url = "https://www.example.com"

    def _check_availability(self) -> None:
        pass


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


def test_init_mocked(mocked_dummy_session: MagicMock, monkeypatch: MonkeyPatch) -> None:
    def _check_availability(self: DummyHTTPConnector) -> None:
        self.request("GET", "_system/check")

    monkeypatch.setattr(DummyHTTPConnector, "_check_availability", _check_availability)

    connector = DummyHTTPConnector.get()
    connector.request("GET", "_system/check")
    assert connector.url == "https://www.example.com"
    assert mocked_dummy_session.request.call_args_list[-1] == call(
        "GET",
        "https://www.example.com/_system/check",
        None,
        timeout=DummyHTTPConnector.TIMEOUT,
        headers={
            "Accept": "application/json",
            "User-Agent": "rki/mex",
        },
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
            {
                "headers": {
                    "Accept": "application/json",
                    "User-Agent": "rki/mex",
                },
            },
        ),
        (
            {},
            MagicMock(status_code=200, json=MagicMock(return_value={"foo": "bar"})),
            {"foo": "bar"},
            {
                "headers": {
                    "Accept": "application/json",
                    "User-Agent": "rki/mex",
                },
            },
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


@pytest.mark.parametrize(
    (
        "fake_response_time",
        "error_or_response",
        "expected_response",
        "expected_retries",
    ),
    [
        (
            0.0,
            RequestException(
                response=Mock(
                    status_code=codes.internal_server_error,
                    json=MagicMock(
                        return_value={"status": codes.internal_server_error}
                    ),
                )
            ),
            "TimedServerError()",
            5,
        ),
        (
            0.0,
            RequestException(
                response=Mock(
                    status_code=codes.too_many_requests,
                    json=MagicMock(return_value={"status": codes.too_many_requests}),
                )
            ),
            "TimedTooManyRequests()",
            5,
        ),
        (
            0.0,
            ConnectTimeout("connect took too long"),
            "ConnectTimeout('connect took too long')",
            3,
        ),
        (
            1.5,
            TimedReadTimeout("read took too long", seconds=1.5),
            "TimedReadTimeout('read took too long')",
            5,
        ),
    ],
    ids=[
        "internal server error",
        "too many requests",
        "connect timeout",
        "timed read timeout",
    ],
)
def test_request_failure(  # noqa: PLR0913
    monkeypatch: MonkeyPatch,
    caplog: LogCaptureFixture,
    fake_response_time: float,
    error_or_response: Exception | Response,
    expected_response: str | dict[str, Any],
    expected_retries: int,
) -> None:
    def mock_request(*_: Any, **__: Any) -> Response:  # noqa: ANN401
        time.sleep(fake_response_time)
        if isinstance(error_or_response, Exception):
            raise error_or_response
        return error_or_response

    mocked_session = MagicMock(spec=requests.Session, name="dummy_session")
    mocked_session.request = mock_request

    def set_mocked_session(self: DummyHTTPConnector) -> None:
        self.session = mocked_session

    monkeypatch.setattr(DummyHTTPConnector, "_set_session", set_mocked_session)

    connector = DummyHTTPConnector.get()

    try:
        response_or_error: Any = connector.request("POST", "things", payload=[])
    except RequestException as error:
        response_or_error = repr(error)

    assert response_or_error == expected_response
    assert len(caplog.messages) == expected_retries
    assert all(
        message.startswith("Backing off _send_request")
        for message in caplog.messages[: expected_retries - 1]
    )
    assert caplog.messages[-1].startswith(
        f"Giving up _send_request(...) after {expected_retries} tries"
    )
