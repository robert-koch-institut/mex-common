from unittest.mock import MagicMock, Mock

from pytest import MonkeyPatch

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.backend_api.models import ItemsContainer
from mex.common.models import ExtractedPerson
from mex.common.sinks.backend_api import BackendApiSink


def test_sink_load_mocked(
    extracted_person: ExtractedPerson, monkeypatch: MonkeyPatch
) -> None:
    def __init__(self: BackendApiConnector) -> None:
        self.session = MagicMock()

    monkeypatch.setattr(BackendApiConnector, "__init__", __init__)

    response = ItemsContainer[ExtractedPerson](items=[extracted_person])
    ingest = Mock(return_value=response)
    monkeypatch.setattr(BackendApiConnector, "ingest", ingest)

    sink = BackendApiSink.get()
    models_or_rule_sets = list(sink.load([extracted_person]))
    assert models_or_rule_sets == [extracted_person]
    ingest.assert_called_once_with([extracted_person])
