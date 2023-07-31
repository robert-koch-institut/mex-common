from unittest.mock import MagicMock

import pytest
from pytest import MonkeyPatch

from mex.common.exceptions import MExError
from mex.common.models import ExtractedPerson
from mex.common.settings import BaseSettings
from mex.common.sinks import Sink
from mex.common.sinks import load as load_module
from mex.common.sinks.load import load


def test_load_multiple(
    monkeypatch: MonkeyPatch, extracted_person: ExtractedPerson
) -> None:
    settings = BaseSettings.get()
    sinks = [Sink.BACKEND, Sink.PUBLIC, Sink.NDJSON]
    monkeypatch.setattr(settings, "sink", sinks)

    models = [extracted_person, extracted_person, extracted_person]

    post_to_backend_api = MagicMock(return_value=[m.identifier for m in models])
    post_to_public_api = MagicMock(return_value=[m.identifier for m in models])
    write_ndjson = MagicMock(return_value=[m.identifier for m in models])
    monkeypatch.setattr(load_module, "post_to_backend_api", post_to_backend_api)
    monkeypatch.setattr(load_module, "post_to_public_api", post_to_public_api)
    monkeypatch.setattr(load_module, "write_ndjson", write_ndjson)

    load(models)

    assert list(post_to_backend_api.call_args[0][0]) == models
    assert list(post_to_public_api.call_args[0][0]) == models
    assert list(write_ndjson.call_args[0][0]) == models


def test_load_unsupported(monkeypatch: MonkeyPatch) -> None:
    settings = BaseSettings.get()
    monkeypatch.setattr(BaseSettings, "__setattr__", object.__setattr__)
    monkeypatch.setattr(settings, "sink", ["bogus-sink"])

    with pytest.raises(MExError, match="Cannot load to bogus-sink."):
        load([])
