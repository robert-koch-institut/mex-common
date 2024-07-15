import json
from unittest.mock import MagicMock, Mock, call

from pytest import MonkeyPatch

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.models import ExtractedPerson
from mex.common.testing import Joker


def test_post_models_mocked(
    monkeypatch: MonkeyPatch, extracted_person: ExtractedPerson
) -> None:
    mocked_send_request = MagicMock(
        spec=BackendApiConnector._send_request,
        return_value=Mock(json=MagicMock(return_value={"identifiers": []})),
    )
    monkeypatch.setattr(BackendApiConnector, "_send_request", mocked_send_request)

    connector = BackendApiConnector.get()
    connector.post_models([extracted_person])

    assert connector.session.headers["X-API-Key"] == "dummy_write_key"
    assert mocked_send_request.call_args_list[-1] == call(
        "POST",
        "http://localhost:8080/v0/ingest",
        None,
        headers={
            "Accept": "application/json",
            "User-Agent": "rki/mex",
        },
        timeout=10,
        data=Joker(),
    )

    assert json.loads(mocked_send_request.call_args_list[-1].kwargs["data"]) == {
        "ExtractedPerson": [
            {
                "identifier": "e3VhxMhEKyjqN5flzLpiEB",
                "hadPrimarySource": "bFQoRhcVH5DHXE",
                "identifierInPrimarySource": "00000000-0000-4000-8000-0000000003de",
                "stableTargetId": "NGwfzG8ROsrvIiQIVDVy",
                "affiliation": ["bFQoRhcVH5DHZg"],
                "email": ["TintzmannM@rki.de"],
                "familyName": ["Tintzmann"],
                "fullName": ["Meinrad I. Tintzmann"],
                "givenName": ["Meinrad"],
                "isniId": ["https://isni.org/isni/0000000109403744"],
                "memberOf": ["bFQoRhcVH5DHV2", "bFQoRhcVH5DHV3"],
                "orcidId": ["https://orcid.org/0000-0002-9079-593X"],
                "entityType": "ExtractedPerson",
            }
        ]
    }
