from typing import Any
from unittest.mock import MagicMock, Mock
from uuid import UUID, uuid4

import pytest
from pytest import MonkeyPatch
from requests import HTTPError

from mex.common.models import ExtractedPerson, ExtractedPrimarySource
from mex.common.public_api.connector import PublicApiConnector
from mex.common.sinks.public_api import post_to_public_api, purge_models_from_public_api


def test_post_to_public_api_mocked(
    extracted_person: ExtractedPerson, monkeypatch: MonkeyPatch
) -> None:
    response = [UUID("00000000-0000-4000-8000-000000339191")]
    monkeypatch.setattr(
        PublicApiConnector,
        "__init__",
        lambda self, settings: setattr(self, "session", MagicMock()),
    )
    post_models = Mock(return_value=response)
    monkeypatch.setattr(PublicApiConnector, "post_models", post_models)

    model_ids = list(post_to_public_api([extracted_person]))
    assert model_ids == response
    post_models.assert_called_once_with([extracted_person])


def test_purge_from_public_api_mocked(
    extracted_person: ExtractedPerson, monkeypatch: MonkeyPatch
) -> None:
    api_id = UUID("00000000-0000-4000-8000-000000339191")
    monkeypatch.setattr(
        PublicApiConnector,
        "__init__",
        lambda self, settings: setattr(self, "session", MagicMock()),
    )
    delete_model = Mock(return_value=api_id)
    monkeypatch.setattr(PublicApiConnector, "delete_model", delete_model)

    messages = list(purge_models_from_public_api([extracted_person]))
    assert len(messages) == 1
    assert messages[0] == (
        f"purged item {api_id} for ExtractedPerson {extracted_person.identifier}"
    )
    delete_model.assert_called_once_with(extracted_person)


@pytest.mark.integration
def test_public_api_post_and_purge_roundtrip(
    extracted_primary_sources: dict[str, ExtractedPrimarySource]
) -> None:
    extracted_person = ExtractedPerson(
        identifierInPrimarySource=str(uuid4()),
        hadPrimarySource=extracted_primary_sources["ldap"].stableTargetId,
        fullName=["Roundtrip Test"],
    )
    try:
        results: list[Any] = list(post_to_public_api([extracted_person]))
        assert len(results) == 1
        results = list(purge_models_from_public_api([extracted_person]))
        assert len(results) == 1
    except HTTPError as error:
        if error.response.json().get("message") == "could not create Solr query":
            pytest.skip("integration test failed due to misconfiguration")
        else:
            raise error
