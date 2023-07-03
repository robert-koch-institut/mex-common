import json
from base64 import b64decode
from unittest.mock import MagicMock, Mock
from uuid import UUID

import pytest
import requests

from mex.common.models.activity import ActivityType, ExtractedActivity
from mex.common.models.person import ExtractedPerson
from mex.common.public_api.connector import PublicApiConnector
from mex.common.public_api.models import PublicApiMetadataItemsResponse
from mex.common.settings import BaseSettings
from mex.common.types import Identifier, Link, Text, Timestamp


def test_authenticate_mocked(mocked_api_session: MagicMock) -> None:
    settings = BaseSettings.get()
    connector = PublicApiConnector.get()
    mocked_api_session.post = mocked_post = MagicMock(
        return_value=Mock(spec=requests.Response)
    )
    mocked_api_session.headers = {}
    mocked_post.return_value.json = MagicMock(
        return_value={
            "access_token": "expected-jwt",
            "expires_in": 300,
            "token_type": "Bearer",
        }
    )

    connector.authenticate()

    mocked_post.assert_called_once_with(
        settings.public_api_token_provider,
        data=b64decode(settings.public_api_token_payload.get_secret_value()),
        timeout=PublicApiConnector.TIMEOUT,
        headers={"Accept": "*/*", "Authorization": None},
    )
    assert connector.session.headers["Authorization"] == "Bearer expected-jwt"


def test_post_models_mocked(
    extracted_person: ExtractedPerson, mocked_api_session: MagicMock
) -> None:
    expected_payload = {
        "items": [
            {
                "entityType": ExtractedPerson.get_entity_type(),
                "values": [
                    {
                        "fieldName": "affiliation",
                        "fieldValue": "bFQoRhcVH5DHZg",
                        "language": None,
                    },
                    {
                        "fieldName": "email",
                        "fieldValue": "TintzmannM@rki.de",
                        "language": None,
                    },
                    {
                        "fieldName": "familyName",
                        "fieldValue": "Tintzmann",
                        "language": None,
                    },
                    {
                        "fieldName": "fullName",
                        "fieldValue": "Meinrad I. Tintzmann",
                        "language": None,
                    },
                    {
                        "fieldName": "givenName",
                        "fieldValue": "Meinrad",
                        "language": None,
                    },
                    {
                        "fieldName": "hadPrimarySource",
                        "fieldValue": "bFQoRhcVH5DHXE",
                        "language": None,
                    },
                    {
                        "fieldName": "identifier",
                        "fieldValue": "bFQoRhcVH5DH3i",
                        "language": None,
                    },
                    {
                        "fieldName": "identifierInPrimarySource",
                        "fieldValue": "00000000-0000-4000-8000-0000000003de",
                        "language": None,
                    },
                    {
                        "fieldName": "isniId",
                        "fieldValue": "https://isni.org/isni/0000000109403744",
                        "language": None,
                    },
                    {
                        "fieldName": "memberOf",
                        "fieldValue": "bFQoRhcVH5DHV2",
                        "language": None,
                    },
                    {
                        "fieldName": "memberOf",
                        "fieldValue": "bFQoRhcVH5DHV3",
                        "language": None,
                    },
                    {
                        "fieldName": "orcidId",
                        "fieldValue": "https://orcid.org/0000-0002-9079-593X",
                        "language": None,
                    },
                    {
                        "fieldName": "stableTargetId",
                        "fieldValue": "bFQoRhcVH5DH8y",
                        "language": None,
                    },
                ],
            }
        ]
    }
    mocked_response = Mock(spec=requests.Response)
    mocked_response.status_code = 201
    mocked_response.json = MagicMock(return_value={"jobId": "000332211bbb"})
    mocked_api_session.request = MagicMock(return_value=mocked_response)

    connector = PublicApiConnector.get()
    connector.post_models([extracted_person], wait_for_done=False)
    payload = json.loads(mocked_api_session.request.call_args.kwargs["data"])

    assert payload == expected_payload


@pytest.mark.integration
def test_search_model_that_does_not_exist() -> None:
    random_id = Identifier.generate()
    connector = PublicApiConnector.get()
    result = connector.search_model(ExtractedActivity, random_id)
    assert result is None


def test_search_model_mocked(mocked_api_session: MagicMock) -> None:
    item_id = UUID("00000000-0000-4000-8000-111111110999")

    activity = ExtractedActivity(
        abstract=[
            Text(value="Dies ist ein deutscher Text."),
            Text(value="And this is in english."),
        ],
        activityType=[ActivityType["SPECIAL_RESEARCH_PROJECT"]],
        alternativeTitle=[Text(value="ᵗʰᵉ ˡᵃⁿᵍᵘᵃᵍᵉ ᵒᶠ ᵗʰᶦˢ ᵗᵉˣᵗ ᶦˢ ʰᵃʳᵈ ᵗᵒ ᵈᵉᵗᵉᶜᵗ")],
        contact=[Identifier("00000000000590")],
        documentation=[Link(url="https://docs.vsli.example.org/en/index.html")],
        end=Timestamp("1970-06-16T16:20:00"),
        externalAssociate=[Identifier("000000000008a1")],
        funderOrCommissioner=[Identifier("00000000000be4")],
        fundingProgram=[],
        responsibleUnit=[
            Identifier("00000000000bf5"),
            Identifier("00000000000bf6"),
        ],
        title=[Text(value="Aperiam debitis similique magnam ipsum neo.")],
        identifierInPrimarySource="activity-1",
        hadPrimarySource=Identifier("00000000100445"),
    )

    mocked_response = Mock(spec=requests.Response)
    mocked_response.status_code = 200
    mocked_response.json = MagicMock(
        return_value={
            "numFound": 1,
            "items": [
                {
                    "itemId": item_id,
                    "entityType": ExtractedActivity.get_entity_type(),
                    "values": [
                        {
                            "fieldName": "abstract",
                            "fieldValue": "Dies ist ein deutscher Text.",
                            "language": "de",
                        },
                        {
                            "fieldName": "abstract",
                            "fieldValue": "And this is in english.",
                            "language": "en",
                        },
                        {
                            "fieldName": "activityType",
                            "fieldValue": "https://mex.rki.de/item/activity-type-5",
                            "language": None,
                        },
                        {
                            "fieldName": "alternativeTitle",
                            "fieldValue": "ᵗʰᵉ ˡᵃⁿᵍᵘᵃᵍᵉ ᵒᶠ ᵗʰᶦˢ ᵗᵉˣᵗ ᶦˢ ʰᵃʳᵈ ᵗᵒ ᵈᵉᵗᵉᶜᵗ",
                            "language": None,
                        },
                        {
                            "fieldName": "contact",
                            "fieldValue": Identifier("00000000000590"),
                            "language": None,
                        },
                        {
                            "fieldName": "documentation",
                            "fieldValue": "https://docs.vsli.example.org/en/index.html",
                            "language": None,
                        },
                        {
                            "fieldName": "end",
                            "fieldValue": Timestamp("1970-06-16T15:20:00Z"),
                            "language": None,
                        },
                        {
                            "fieldName": "externalAssociate",
                            "fieldValue": Identifier("000000000008a1"),
                            "language": None,
                        },
                        {
                            "fieldName": "funderOrCommissioner",
                            "fieldValue": Identifier("00000000000be4"),
                            "language": None,
                        },
                        {
                            "fieldName": "hadPrimarySource",
                            "fieldValue": activity.hadPrimarySource,
                            "language": None,
                        },
                        {
                            "fieldName": "identifier",
                            "fieldValue": activity.identifier,
                            "language": None,
                        },
                        {
                            "fieldName": "identifierInPrimarySource",
                            "fieldValue": activity.identifierInPrimarySource,
                            "language": None,
                        },
                        {
                            "fieldName": "responsibleUnit",
                            "fieldValue": Identifier("00000000000bf5"),
                            "language": None,
                        },
                        {
                            "fieldName": "responsibleUnit",
                            "fieldValue": Identifier("00000000000bf6"),
                            "language": None,
                        },
                        {
                            "fieldName": "stableTargetId",
                            "fieldValue": activity.stableTargetId,
                            "language": None,
                        },
                        {
                            "fieldName": "title",
                            "fieldValue": "Aperiam debitis similique magnam ipsum neo.",
                            "language": None,
                        },
                    ],
                }
            ],
        }
    )
    mocked_api_session.request = MagicMock(return_value=mocked_response)

    connector = PublicApiConnector.get()
    model = connector.search_model(ExtractedActivity, item_id)

    assert model is not None
    assert model == activity


def test_get_all_items_mocked(
    mocked_api_session: MagicMock,
    mex_metadata_items_response: PublicApiMetadataItemsResponse,
) -> None:
    response_data = {
        "items": [
            {
                "itemId": "00005da9-f653-4c9c-b123-7b555d36b0fd",
                "entityType": "Datum",
            },
            {
                "itemId": "000054a2-b16a-4f4e-82d2-1a222dba41e6",
                "entityType": "ExtractedDatum",
            },
            {
                "itemId": "000054a2-b16a-4f4e-82d2-1a222fba41e6",
                "entityType": "ExtractedPerson",
            },
            {
                "itemId": "000054a3-b16a-4f4e-82d2-1a222fbc41e6",
                "entityType": "Person",
            },
        ],
        "next": "",
    }
    mocked_response = Mock(spec=requests.Response)
    mocked_response.status_code = 200
    mocked_response.json = MagicMock(return_value=response_data)
    mocked_api_session.request = MagicMock(return_value=mocked_response)
    connector = PublicApiConnector.get()
    items = connector.get_all_items()
    assert items == mex_metadata_items_response


@pytest.mark.integration
def test_get_all_items() -> None:
    connector = PublicApiConnector.get()
    initial_items = connector.get_all_items()

    # check for correct first item on second page only if there is a second page
    if next_item_id := initial_items.next:
        next_items = connector.get_all_items(offset_item_id=next_item_id)
        assert next_items.items[0].itemId == next_item_id
