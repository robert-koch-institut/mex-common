from unittest.mock import MagicMock, Mock, call

import pytest
import requests
from pytest import MonkeyPatch

from mex.common.connector import (
    ConnectorContext,
    HTTPConnector,
    reset_connector_context,
)
from mex.common.settings import BaseSettings


class DummyConnector(HTTPConnector):
    def _set_url(self, settings: BaseSettings) -> None:
        self.url = "https://www.example.com"

    def _check_availability(self) -> None:
        self.request("GET", "_system/check")

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def mocked_dummy_session(monkeypatch: MonkeyPatch) -> MagicMock:
    """Mock the DummyConnector with a MagicMock session and return that."""
    mocked_session = MagicMock(spec=requests.Session, name="dummy_session")
    mocked_session.request = MagicMock(
        return_value=Mock(spec=requests.Response, status_code=200)
    )

    def set_mocked_session(self: DummyConnector, settings: BaseSettings) -> None:
        self.session = mocked_session

    monkeypatch.setattr(DummyConnector, "_set_session", set_mocked_session)
    return mocked_session


@pytest.mark.integration
def test_connector_enter_returns_self() -> None:
    dummy = DummyConnector.get()
    with dummy as entered_dummy:
        assert dummy is entered_dummy


@pytest.mark.usefixtures("mocked_dummy_session")
def test_connector_enter_returns_self_mocked() -> None:
    dummy = DummyConnector.get()
    with dummy as entered_dummy:
        assert dummy is entered_dummy


def test_init_mocked(mocked_dummy_session: MagicMock) -> None:
    connector = DummyConnector.get()
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
def test_connector_exit_closes_itself_and_removes_from_context() -> None:
    dummy = DummyConnector.get()
    assert DummyConnector in ConnectorContext.get()
    with dummy:
        pass
    assert dummy.closed
    assert DummyConnector not in ConnectorContext.get()


@pytest.mark.usefixtures("mocked_dummy_session")
def test_connector_reset_context() -> None:
    DummyConnector.get()
    assert len(ConnectorContext.get()) == 1

    reset_connector_context()

    assert len(ConnectorContext.get()) == 0
