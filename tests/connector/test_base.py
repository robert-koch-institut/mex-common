from mex.common.connector import (
    BaseConnector,
    ConnectorContext,
    reset_connector_context,
)


class DummyConnector(BaseConnector):
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


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
