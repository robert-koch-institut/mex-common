from unittest.mock import MagicMock, Mock
from uuid import UUID

from pytest import MonkeyPatch

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import ExtractedPerson
from mex.common.settings import BaseSettings
from mex.common.sinks.backend_api import post_to_backend_api


def test_post_to_backend_api_mocked(
    extracted_person: ExtractedPerson, monkeypatch: MonkeyPatch
) -> None:
    def __init__(self: BackendApiConnector, settings: BaseSettings) -> None:
        self.session = MagicMock()

    monkeypatch.setattr(BackendApiConnector, "__init__", __init__)

    response = [UUID("00000000-0000-4000-8000-000000339191")]
    post_models = Mock(return_value=response)
    monkeypatch.setattr(BackendApiConnector, "post_models", post_models)

    model_ids = list(post_to_backend_api([extracted_person]))
    assert model_ids == response
    post_models.assert_called_once_with([extracted_person])
