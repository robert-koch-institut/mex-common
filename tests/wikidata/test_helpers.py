from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from mex.common.models import ExtractedOrganization, ExtractedPrimarySource
from mex.common.wikidata import helpers
from mex.common.wikidata.extract import search_organization_by_label
from mex.common.wikidata.helpers import get_extracted_organization_from_wikidata
from mex.common.wikidata.models.organization import WikidataOrganization
from mex.common.wikidata.transform import (
    transform_wikidata_organization_to_extracted_organization,
)


@pytest.mark.usefixtures(
    "mocked_wikidata",
)
def test_get_extracted_organization_from_wikidata(
    wikidata_organization: WikidataOrganization,
    extracted_primary_sources: dict[str, ExtractedPrimarySource],
    monkeypatch: MonkeyPatch,
) -> None:
    query_string = "Robert Koch-Institut"
    wikidata_primary_source = extracted_primary_sources["wikidata"]
    extracted_wikidata_organization = (
        transform_wikidata_organization_to_extracted_organization(
            wikidata_organization, wikidata_primary_source
        )
    )
    assert isinstance(extracted_wikidata_organization, ExtractedOrganization)

    # mock all the things
    mocked_search_organization_by_label = Mock(side_effect=search_organization_by_label)
    monkeypatch.setattr(
        helpers, "search_organization_by_label", mocked_search_organization_by_label
    )
    mocked_transform_wikidata_organization_to_extracted_organization = Mock(
        side_effect=transform_wikidata_organization_to_extracted_organization
    )
    monkeypatch.setattr(
        helpers,
        "transform_wikidata_organization_to_extracted_organization",
        mocked_transform_wikidata_organization_to_extracted_organization,
    )

    # organization found and transformed
    returned = get_extracted_organization_from_wikidata(
        query_string, wikidata_primary_source
    )
    assert returned == extracted_wikidata_organization
    mocked_search_organization_by_label.assert_called_once_with(query_string)
    mocked_transform_wikidata_organization_to_extracted_organization.assert_called_once_with(
        wikidata_organization, wikidata_primary_source
    )
