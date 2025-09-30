from mex.common.connector import CONNECTOR_STORE, BaseConnector


class DummyConnector(BaseConnector):
    def __init__(self) -> None:
        self.closed = False

    def metrics(self) -> dict[str, int]:
        return {"foo": 42}

    def close(self) -> None:
        self.closed = True


def test_connector_get() -> None:
    assert len(list(CONNECTOR_STORE)) == 0

    connector = DummyConnector.get()
    assert isinstance(connector, DummyConnector)

    assert len(list(CONNECTOR_STORE)) == 1

    assert DummyConnector.get() is connector


def test_connector_store_reset() -> None:
    connector = DummyConnector.get()
    assert len(list(CONNECTOR_STORE)) == 1

    CONNECTOR_STORE.reset()

    assert connector.closed is True
    assert len(list(CONNECTOR_STORE)) == 0


def test_connector_store_metrics() -> None:
    DummyConnector.get()
    assert len(list(CONNECTOR_STORE)) == 1

    assert CONNECTOR_STORE.metrics() == {"dummy_connector_foo": 42}

    CONNECTOR_STORE.reset()
    assert CONNECTOR_STORE.metrics() == {}
