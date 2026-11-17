from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from mex.common.primary_source.helpers import (
    get_extracted_primary_source_by_name,
)
from mex.common.wikidata import helpers
from mex.common.wikidata.models import (
    WikidataLocation,
    WikidataOrganization,
)


@pytest.mark.parametrize(
    "country_qids",
    [
        [],
        ["Q183"],
        ["Q183", "Q30"],
        ["Q183", "Q183"],
    ],
    ids=["no_countries", "one_country", "two_countries", "double_QIDs"],
)
def test_get_wikidata_organization_with_locations(
    monkeypatch: MonkeyPatch,
    country_qids: list[str],
) -> None:
    """Return an organization and its unique country locations."""
    primary_source = get_extracted_primary_source_by_name("wikidata")
    assert primary_source is not None

    wikidata_organization = WikidataOrganization.model_validate(
        {
            "id": "Q679041",
            "labels": {"de": {"language": "de", "value": "Robert Koch-Institut"}},
            "aliases": {},
            "claims": {
                "P17": [
                    {"mainsnak": {"datavalue": {"value": {"id": qid}}}}
                    for qid in country_qids
                ]
            },
        }
    )

    wikidata_locations = {
        "Q183": WikidataLocation.model_validate(
            {
                "id": "Q183",
                "labels": {"de": {"language": "de", "value": "Deutschland"}},
                "claims": {},
            }
        ),
        "Q30": WikidataLocation.model_validate(
            {
                "id": "Q30",
                "labels": {"de": {"language": "de", "value": "Vereinigte Staaten"}},
                "claims": {},
            }
        ),
    }

    mocked_get_organization = Mock(return_value=wikidata_organization)
    mocked_get_location = Mock(side_effect=lambda qid: wikidata_locations[qid])

    monkeypatch.setattr(
        helpers,
        "get_extracted_primary_source_by_name",
        Mock(return_value=primary_source),
    )
    monkeypatch.setattr(
        helpers,
        "get_wikidata_organization",
        mocked_get_organization,
    )
    monkeypatch.setattr(
        helpers,
        "get_wikidata_location",
        mocked_get_location,
    )

    result = helpers.get_wikidata_organization_with_locations("Q679041")

    assert result is not None
    assert result.primary_source == primary_source

    assert result.organization.identifierInPrimarySource == "Q679041"
    assert result.organization.hadPrimarySource == primary_source.stableTargetId

    expected_qids = set(country_qids)

    assert [
        location.identifierInPrimarySource for location in result.locations
    ] == list(expected_qids)

    assert all(
        location.hadPrimarySource == primary_source.stableTargetId
        for location in result.locations
    )

    assert result.organization.country == [
        location.stableTargetId for location in result.locations
    ]

    mocked_get_organization.assert_called_once_with("Q679041")
    assert mocked_get_location.call_count == len(expected_qids)
