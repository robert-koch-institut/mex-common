from unittest.mock import MagicMock
from uuid import UUID

import pytest
from pytest import MonkeyPatch

from mex.common.exceptions import MExError
from mex.common.public_api.connector import PublicApiConnector
from mex.common.public_api.extract import extract_mex_person_items
from mex.common.public_api.models import PublicApiMetadataItemsResponse


@pytest.mark.integration
def test_extract_mex_person_items() -> None:
    mex_persons = list(extract_mex_person_items())
    assert all(p.entityType in ["Person", "ExtractedPerson"] for p in mex_persons)


def test_extract_mex_person_items_mocked(
    mex_metadata_items_response: PublicApiMetadataItemsResponse,
    monkeypatch: MonkeyPatch,
) -> None:
    mex_metadata_items_response_with_next = mex_metadata_items_response.model_copy()
    mex_metadata_items_response_with_next.next = UUID(
        "3fcce11e80e920b410efd0c919001a31"
    )
    get_all_items = MagicMock(
        side_effect=[mex_metadata_items_response_with_next, mex_metadata_items_response]
    )
    monkeypatch.setattr(PublicApiConnector, "get_all_items", get_all_items)
    monkeypatch.setattr(
        PublicApiConnector,
        "__init__",
        lambda self, _: setattr(self, "session", MagicMock()),
    )

    mex_persons = list(extract_mex_person_items())
    assert mex_persons == mex_metadata_items_response.items[2:4] * 2


@pytest.mark.integration
def test_extract_mex_person_items_limit_reached(
    mex_metadata_items_response: PublicApiMetadataItemsResponse,
    monkeypatch: MonkeyPatch,
) -> None:
    mex_metadata_items_response.next = UUID("3fcce11e80e920b410efd0c919001a31")
    get_all_items = MagicMock(side_effect=[mex_metadata_items_response] * 101)
    monkeypatch.setattr(PublicApiConnector, "get_all_items", get_all_items)
    monkeypatch.setattr(
        PublicApiConnector,
        "__init__",
        lambda self, _: setattr(self, "session", MagicMock()),
    )

    with pytest.raises(MExError):
        list(extract_mex_person_items())
