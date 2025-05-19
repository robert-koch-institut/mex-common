import json
from unittest.mock import MagicMock, call

import pytest
from requests.exceptions import HTTPError

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import (
    AnyExtractedModel,
    AnyPreviewModel,
    ExtractedPerson,
    ItemsContainer,
    MergedPerson,
    PaginatedItemsContainer,
    PersonRuleSetRequest,
    PersonRuleSetResponse,
    PreviewPerson,
)
from mex.common.testing import Joker


@pytest.mark.usefixtures("mocked_backend")
def test_set_authentication_mocked() -> None:
    connector = BackendApiConnector.get()
    assert connector.session.headers["X-API-Key"] == "dummy_write_key"


def test_ingest_mocked(
    mocked_backend: MagicMock, extracted_person: ExtractedPerson
) -> None:
    mocked_return = {"items": [extracted_person]}
    mocked_backend.return_value.json.return_value = mocked_return

    connector = BackendApiConnector.get()
    connector.ingest([extracted_person])

    assert mocked_backend.call_args == call(
        "POST",
        "http://localhost:8080/v0/ingest",
        None,
        headers={
            "Accept": "application/json",
            "User-Agent": "rki/mex",
        },
        data=Joker(),
        timeout=10,
    )
    assert (
        json.loads(mocked_backend.call_args.kwargs["data"])
        == ItemsContainer[AnyExtractedModel](items=[extracted_person]).model_dump()
    )


def test_fetch_extracted_items_mocked(
    mocked_backend: MagicMock, extracted_person: ExtractedPerson
) -> None:
    mocked_return = {"items": [extracted_person.model_dump()], "total": 3}
    mocked_backend.return_value.json.return_value = mocked_return

    connector = BackendApiConnector.get()
    response = connector.fetch_extracted_items(
        "Tintzmann",
        "NGwfzG8ROsrvIiQIVDVy",
        entity_type=["ExtractedPerson", "ExtractedContactPoint"],
        skip=0,
        limit=1,
    )

    assert response.items == [extracted_person]
    assert response.total == 3

    assert mocked_backend.call_args == call(
        "GET",
        "http://localhost:8080/v0/extracted-item",
        {
            "q": "Tintzmann",
            "stableTargetId": "NGwfzG8ROsrvIiQIVDVy",
            "entityType": ["ExtractedPerson", "ExtractedContactPoint"],
            "skip": "0",
            "limit": "1",
        },
        headers={
            "Accept": "application/json",
            "User-Agent": "rki/mex",
        },
        timeout=10,
    )


def test_fetch_merged_items_mocked(
    mocked_backend: MagicMock, merged_person: MergedPerson
) -> None:
    mocked_return = {"items": [merged_person.model_dump()], "total": 3}
    mocked_backend.return_value.json.return_value = mocked_return

    connector = BackendApiConnector.get()
    response = connector.fetch_merged_items(
        "Tintzmann",
        entity_type=["MergedPerson", "MergedContactPoint"],
        had_primary_source=None,
        skip=0,
        limit=1,
    )

    assert response.items == [merged_person]
    assert response.total == 3

    assert mocked_backend.call_args == call(
        "GET",
        "http://localhost:8080/v0/merged-item",
        {
            "q": "Tintzmann",
            "entityType": ["MergedPerson", "MergedContactPoint"],
            "hadPrimarySource": None,
            "skip": "0",
            "limit": "1",
        },
        headers={
            "Accept": "application/json",
            "User-Agent": "rki/mex",
        },
        timeout=10,
    )


def test_get_merged_item_mocked(
    mocked_backend: MagicMock, merged_person: MergedPerson
) -> None:
    mocked_return = {"items": [merged_person.model_dump()], "total": 1}
    mocked_backend.return_value.json.return_value = mocked_return

    connector = BackendApiConnector.get()
    response = connector.get_merged_item("NGwfzG8ROsrvIiQIVDVy")

    assert response == merged_person

    assert mocked_backend.call_args == call(
        "GET",
        "http://localhost:8080/v0/merged-item",
        {
            "identifier": "NGwfzG8ROsrvIiQIVDVy",
            "limit": "1",
        },
        headers={
            "Accept": "application/json",
            "User-Agent": "rki/mex",
        },
        timeout=10,
    )


def test_get_merged_item_error_mocked(mocked_backend: MagicMock) -> None:
    mocked_return = {"items": [], "total": 0}
    mocked_backend.return_value.json.return_value = mocked_return

    connector = BackendApiConnector.get()
    with pytest.raises(HTTPError, match="merged item was not found"):
        connector.get_merged_item("NGwfzG8ROsrvIiQIVDVy")

    assert mocked_backend.call_args == call(
        "GET",
        "http://localhost:8080/v0/merged-item",
        {
            "identifier": "NGwfzG8ROsrvIiQIVDVy",
            "limit": "1",
        },
        headers={
            "Accept": "application/json",
            "User-Agent": "rki/mex",
        },
        timeout=10,
    )


def test_preview_merged_item_mocked(
    mocked_backend: MagicMock,
    preview_person: PreviewPerson,
    rule_set_request: PersonRuleSetRequest,
) -> None:
    mocked_return = preview_person.model_dump()
    mocked_backend.return_value.json.return_value = mocked_return

    connector = BackendApiConnector.get()
    response = connector.preview_merged_item("NGwfzG8ROsrvIiQIVDVy", rule_set_request)

    assert response == preview_person

    assert mocked_backend.call_args == call(
        "POST",
        "http://localhost:8080/v0/preview-item/NGwfzG8ROsrvIiQIVDVy",
        None,
        headers={
            "Accept": "application/json",
            "User-Agent": "rki/mex",
        },
        timeout=10,
        data=Joker(),
    )
    assert (
        json.loads(mocked_backend.call_args.kwargs["data"])
        == rule_set_request.model_dump()
    )


def test_fetch_preview_items_mocked(
    mocked_backend: MagicMock,
    preview_person: PreviewPerson,
) -> None:
    preview_response = PaginatedItemsContainer[AnyPreviewModel](
        items=[preview_person], total=92
    )
    mocked_return = preview_response.model_dump()
    mocked_backend.return_value.json.return_value = mocked_return

    connector = BackendApiConnector.get()
    response = connector.fetch_preview_items("foobar", None, None, 1, 0)

    assert response == preview_response

    assert mocked_backend.call_args == call(
        "GET",
        "http://localhost:8080/v0/preview-item",
        {
            "q": "foobar",
            "entityType": None,
            "hadPrimarySource": None,
            "skip": "1",
            "limit": "0",
        },
        timeout=10,
        headers={
            "Accept": "application/json",
            "User-Agent": "rki/mex",
        },
    )


def test_get_rule_set_mocked(
    mocked_backend: MagicMock, rule_set_response: PersonRuleSetResponse
) -> None:
    mocked_backend.return_value.json.return_value = rule_set_response.model_dump()

    connector = BackendApiConnector.get()
    response = connector.get_rule_set("NGwfzG8ROsrvIiQIVDVy")

    assert response == rule_set_response

    assert mocked_backend.call_args == call(
        "GET",
        "http://localhost:8080/v0/rule-set/NGwfzG8ROsrvIiQIVDVy",
        None,
        headers={
            "Accept": "application/json",
            "User-Agent": "rki/mex",
        },
        timeout=10,
    )
