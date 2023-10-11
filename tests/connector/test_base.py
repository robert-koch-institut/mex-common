import pytest

from mex.common.connector import (
    BaseConnector,
    ConnectorContext,
    reset_connector_context,
)
from mex.common.settings import BaseSettings


class DummySettings(BaseSettings):
    configuration: str = "DEFAULT_123"


@pytest.fixture(autouse=True)
def settings() -> DummySettings:
    """Load the settings for this pytest session."""
    return DummySettings.get()


class DummyConnector(BaseConnector):
    def __init__(self, settings: DummySettings) -> None:
        self.config = settings.configuration
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_connector_infers_correct_settings_class() -> None:
    settings = DummySettings.get()
    settings.configuration = "VALUE_456"

    dummy = DummyConnector.get()
    assert dummy.config == "VALUE_456"


def test_connector_enter_returns_self() -> None:
    dummy = DummyConnector.get()
    with dummy as entered_dummy:
        assert dummy is entered_dummy


def test_connector_exit_closes_itself_and_removes_from_context() -> None:
    dummy = DummyConnector.get()
    assert DummyConnector in ConnectorContext.get()
    with dummy:
        pass
    assert dummy.closed
    assert DummyConnector not in ConnectorContext.get()


def test_connector_reset_context() -> None:
    DummyConnector.get()
    assert len(ConnectorContext.get()) == 1

    reset_connector_context()

    assert len(ConnectorContext.get()) == 0
