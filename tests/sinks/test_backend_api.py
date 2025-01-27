from unittest.mock import MagicMock, Mock

from pytest import MonkeyPatch

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.backend_api.models import IdentifiersResponse
from mex.common.models import ExtractedPerson
from mex.common.sinks.backend_api import BackendApiSink


def test_sink_load_mocked(
    extracted_person: ExtractedPerson, monkeypatch: MonkeyPatch
) -> None:
    def __init__(self: BackendApiConnector) -> None:
        self.session = MagicMock()

    monkeypatch.setattr(BackendApiConnector, "__init__", __init__)

    response = IdentifiersResponse(identifiers=[extracted_person.identifier])
    post_extracted_items = Mock(return_value=response)
    monkeypatch.setattr(
        BackendApiConnector, "post_extracted_items", post_extracted_items
    )

    sink = BackendApiSink.get()
    model_ids = list(sink.load([extracted_person]))
    assert model_ids == response.identifiers
    post_extracted_items.assert_called_once_with([extracted_person])
