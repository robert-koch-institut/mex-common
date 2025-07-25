import json
from unittest.mock import MagicMock, call

import pytest

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
        query_string="Tintzmann",
        stable_target_id="NGwfzG8ROsrvIiQIVDVy",
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
            "referenceField": None,
            "referencedIdentifier": None,
            "skip": "0",
            "limit": "1",
        },
        headers={
            "Accept": "application/json",
            "User-Agent": "rki/mex",
        },
        timeout=10,
    )


def test_get_extracted_item_mocked(
    mocked_backend: MagicMock, extracted_person: ExtractedPerson
) -> None:
    mocked_return = extracted_person.model_dump()
    mocked_backend.return_value.json.return_value = mocked_return

    connector = BackendApiConnector.get()
    response = connector.get_extracted_item("e3VhxMhEKyjqN5flzLpiEB")

    assert response == extracted_person

    assert mocked_backend.call_args == call(
        "GET",
        "http://localhost:8080/v0/extracted-item/e3VhxMhEKyjqN5flzLpiEB",
        None,
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
        query_string="Tintzmann",
        entity_type=["MergedPerson", "MergedContactPoint"],
        limit=1,
    )

    assert response.items == [merged_person]
    assert response.total == 3

    assert mocked_backend.call_args == call(
        "GET",
        "http://localhost:8080/v0/merged-item",
        {
            "q": "Tintzmann",
            "identifier": None,
            "entityType": ["MergedPerson", "MergedContactPoint"],
            "referenceField": None,
            "referencedIdentifier": None,
            "skip": "0",
            "limit": "1",
        },
        headers={
            "Accept": "application/json",
            "User-Agent": "rki/mex",
        },
        timeout=10,
    )


def test_fetch_all_merged_items_mocked(
    mocked_backend: MagicMock, merged_person: MergedPerson
) -> None:
    merged_person_json = merged_person.model_dump()
    mocked_backend.return_value.json.side_effect = [
        {"status": "ok"},  # status check
        {"items": [], "total": 103},  # call to gauge the total
        {"items": [merged_person_json] * 100, "total": 103},  # first page 0-99
        {"items": [merged_person_json] * 3, "total": 103},  # second page 100-103
    ]

    connector = BackendApiConnector.get()
    items = list(connector.fetch_all_merged_items(query_string="Tintzmann"))

    # expect 4 calls: status check, get the total, and get two pages 0-99/100-103
    assert len(mocked_backend.call_args_list) == 4

    # expect all 103 persons to be there
    assert items == [merged_person] * 103

    # expect the last call to be made with the correct parameters
    assert mocked_backend.call_args == call(
        "GET",
        "http://localhost:8080/v0/merged-item",
        {
            "q": "Tintzmann",
            "identifier": None,
            "entityType": None,
            "referenceField": None,
            "referencedIdentifier": None,
            "skip": "100",
            "limit": "100",
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
    mocked_return = merged_person.model_dump()
    mocked_backend.return_value.json.return_value = mocked_return

    connector = BackendApiConnector.get()
    response = connector.get_merged_item("NGwfzG8ROsrvIiQIVDVy")

    assert response == merged_person

    assert mocked_backend.call_args == call(
        "GET",
        "http://localhost:8080/v0/merged-item/NGwfzG8ROsrvIiQIVDVy",
        None,
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
    response = connector.fetch_preview_items(query_string="foobar", limit=1)

    assert response == preview_response

    assert mocked_backend.call_args == call(
        "GET",
        "http://localhost:8080/v0/preview-item",
        {
            "q": "foobar",
            "identifier": None,
            "entityType": None,
            "referenceField": None,
            "referencedIdentifier": None,
            "skip": "0",
            "limit": "1",
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
