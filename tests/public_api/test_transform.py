from typing import Any, Optional

import pytest
from pytest import MonkeyPatch

from mex.common.models import EXTRACTED_MODEL_CLASSES_BY_NAME, MExModel
from mex.common.public_api.models import PublicApiItem
from mex.common.public_api.transform import (
    transform_mex_model_to_public_api_item,
    transform_public_api_item_to_mex_model,
)
from mex.common.types import (
    Identifier,
    Link,
    LinkLanguage,
    OrganizationID,
    PersonID,
    Text,
    TextLanguage,
    Timestamp,
)


class DummyModel(MExModel):
    stableTargetId: Identifier
    optional: Optional[str]
    oneString: str
    manyStrings: list[str]
    oneText: Text
    manyTexts: list[Text]
    oneLink: Link
    manyLinks: list[Link]
    reference: Identifier
    manyReferences: list[PersonID | OrganizationID]
    timestamp: Timestamp

    @classmethod
    def get_entity_type(cls) -> str:
        return cls.__name__


@pytest.fixture
def raw_mex_model() -> dict[str, Any]:
    return {
        "identifier": Identifier("0000000000046f"),
        "stableTargetId": Identifier("00000000000fds"),
        "manyLinks": [
            {
                "title": "Example PDF",
                "url": "file:///C:/Users/John%20Doe/example.pdf",
            },
            {"language": LinkLanguage.DE, "url": "https://foo-bar-beispiel.de"},
        ],
        "manyReferences": [
            Identifier("00000000001eac"),
            Identifier("00000000001ead"),
        ],
        "manyStrings": ["red", "blue"],
        "manyTexts": [
            {"value": "El burro patea."},
            {"language": TextLanguage.DE, "value": "Der Fuchs springt."},
        ],
        "oneLink": {"language": LinkLanguage.EN, "url": "https://www.example.com"},
        "oneString": "grün",
        "oneText": {"language": TextLanguage.EN, "value": "The lion sleeps."},
        "reference": Identifier("00000000001eab"),
        "timestamp": Timestamp("2010-12-24T22:00"),
    }


@pytest.fixture
def raw_api_item() -> dict[str, Any]:
    return {
        "entityType": "DummyModel",
        "values": [
            {
                "fieldName": "identifier",
                "fieldValue": Identifier("0000000000046f"),
            },
            {
                "fieldName": "manyLinks",
                "fieldValue": "[Example PDF](file:///C:/Users/John%20Doe/example\\.pdf)",
            },
            {
                "fieldName": "manyLinks",
                "fieldValue": "https://foo-bar-beispiel.de",
                "language": "de",
            },
            {
                "fieldName": "manyReferences",
                "fieldValue": Identifier("00000000001eac"),
            },
            {
                "fieldName": "manyReferences",
                "fieldValue": Identifier("00000000001ead"),
            },
            {"fieldName": "manyStrings", "fieldValue": "red"},
            {"fieldName": "manyStrings", "fieldValue": "blue"},
            {"fieldName": "manyTexts", "fieldValue": "El burro patea."},
            {
                "fieldName": "manyTexts",
                "fieldValue": "Der Fuchs springt.",
                "language": "de",
            },
            {
                "fieldName": "oneLink",
                "fieldValue": "https://www.example.com",
                "language": "en",
            },
            {"fieldName": "oneString", "fieldValue": "grün"},
            {
                "fieldName": "oneText",
                "fieldValue": "The lion sleeps.",
                "language": "en",
            },
            {
                "fieldName": "reference",
                "fieldValue": Identifier("00000000001eab"),
            },
            {"fieldName": "stableTargetId", "fieldValue": Identifier("00000000000fds")},
            {
                "fieldName": "timestamp",
                "fieldValue": Timestamp("2010-12-24T22:00"),
            },
        ],
    }


def test_transform_mex_model_to_public_api_item(
    raw_mex_model: dict[str, Any], raw_api_item: dict[str, Any]
) -> None:
    # optional field will be omitted
    dummy_model = DummyModel(optional=None, **raw_mex_model)

    dummy_item = transform_mex_model_to_public_api_item(dummy_model)

    assert dummy_item.dict(exclude_none=True) == raw_api_item


def test_transform_public_api_item_to_mex_model(
    monkeypatch: MonkeyPatch,
    raw_api_item: dict[str, Any],
    raw_mex_model: dict[str, Any],
) -> None:
    monkeypatch.setitem(
        EXTRACTED_MODEL_CLASSES_BY_NAME, DummyModel.get_entity_type(), DummyModel
    )
    dummy_item = PublicApiItem(**raw_api_item, businessId="00000000000fds")

    dummy_model = transform_public_api_item_to_mex_model(dummy_item)

    assert dummy_model
    assert dummy_model.dict(exclude_none=True) == raw_mex_model


def test_transform_public_api_item_to_mex_model_unknown() -> None:
    api_item = PublicApiItem(
        entityType="UnknownModel", values=[], businessId="a00b02800211BD90"
    )
    returned = transform_public_api_item_to_mex_model(api_item)
    assert returned is None
