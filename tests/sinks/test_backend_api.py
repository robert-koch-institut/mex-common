from unittest.mock import MagicMock, Mock

import pytest
from pytest import MonkeyPatch

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import ExtractedPerson, MergedPerson
from mex.common.sinks.backend_api import BackendApiSink


def test_sink_load_mocked(
    extracted_person: ExtractedPerson, monkeypatch: MonkeyPatch
) -> None:
    def __init__(self: BackendApiConnector) -> None:
        self.session = MagicMock()

    monkeypatch.setattr(BackendApiConnector, "__init__", __init__)

    ingest = Mock(return_value=[extracted_person])
    monkeypatch.setattr(BackendApiConnector, "ingest", ingest)

    sink = BackendApiSink.get()
    models_or_rule_sets = list(sink.load([extracted_person]))
    assert models_or_rule_sets == [extracted_person]
    ingest.assert_called_once_with([extracted_person], timeout=(5, 90))


def test_sink_load_merged_error(
    merged_person: MergedPerson, monkeypatch: MonkeyPatch
) -> None:
    def __init__(self: BackendApiConnector) -> None:
        self.session = MagicMock()

    monkeypatch.setattr(BackendApiConnector, "__init__", __init__)

    sink = BackendApiSink.get()
    with pytest.raises(NotImplementedError, match="backend cannot"):
        list(sink.load([merged_person]))
