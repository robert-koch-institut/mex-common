from unittest.mock import MagicMock, Mock

import pytest
from pytest import MonkeyPatch

from mex.common.backend_api.connector import BackendApiConnector


@pytest.fixture
def mocked_backend(monkeypatch: MonkeyPatch) -> MagicMock:
    """Return the mocked request dispatch method of backend connector."""
    mocked_send_request = MagicMock(
        spec=BackendApiConnector._send_request,
        return_value=Mock(json=MagicMock(return_value={})),
        name="mocked_backend_send_request",
    )
    monkeypatch.setattr(BackendApiConnector, "_send_request", mocked_send_request)
    return mocked_send_request
