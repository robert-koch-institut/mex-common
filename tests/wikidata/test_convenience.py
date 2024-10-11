from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from mex.common.models import ExtractedOrganization, ExtractedPrimarySource
from mex.common.wikidata import convenience
from mex.common.wikidata.convenience import (
    _ORGANIZATION_BY_QUERY_CACHE,
    get_merged_organization_id_by_query_with_extract_transform_and_load,
)
from mex.common.wikidata.extract import search_organization_by_label
from mex.common.wikidata.models.organization import WikidataOrganization
from mex.common.wikidata.transform import (
    transform_wikidata_organization_to_extracted_organization,
)


@pytest.mark.usefixtures(
    "mocked_wikidata",
)
def test_get_merged_organization_id_by_query_with_extract_transform_and_load_mocked(
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
        convenience, "search_organization_by_label", mocked_search_organization_by_label
    )
    mocked_transform_wikidata_organization_to_extracted_organization = Mock(
        side_effect=transform_wikidata_organization_to_extracted_organization
    )
    monkeypatch.setattr(
        convenience,
        "transform_wikidata_organization_to_extracted_organization",
        mocked_transform_wikidata_organization_to_extracted_organization,
    )
    load_function = Mock()

    # organization found and transformed
    _ORGANIZATION_BY_QUERY_CACHE.clear()
    returned = get_merged_organization_id_by_query_with_extract_transform_and_load(
        query_string, wikidata_primary_source, load_function
    )
    assert returned == extracted_wikidata_organization.stableTargetId
    mocked_search_organization_by_label.assert_called_once_with(query_string)
    mocked_transform_wikidata_organization_to_extracted_organization.assert_called_once_with(
        wikidata_organization, wikidata_primary_source
    )
    load_function.assert_called_once_with([extracted_wikidata_organization])

    # make sure caching works
    mocked_search_organization_by_label.reset_mock()
    mocked_transform_wikidata_organization_to_extracted_organization.reset_mock()
    load_function.reset_mock()
    returned = get_merged_organization_id_by_query_with_extract_transform_and_load(
        query_string, wikidata_primary_source, load_function
    )
    assert returned == extracted_wikidata_organization.stableTargetId
    mocked_search_organization_by_label.assert_not_called()
    mocked_transform_wikidata_organization_to_extracted_organization.assert_not_called()
    load_function.assert_not_called()

    # make sure cache is reset for different load function
    mocked_search_organization_by_label.reset_mock()
    mocked_transform_wikidata_organization_to_extracted_organization.reset_mock()
    load_function = Mock()
    returned = get_merged_organization_id_by_query_with_extract_transform_and_load(
        query_string, wikidata_primary_source, load_function
    )
    assert returned == extracted_wikidata_organization.stableTargetId
    mocked_search_organization_by_label.assert_called_once_with(query_string)
    mocked_transform_wikidata_organization_to_extracted_organization.assert_called_once_with(
        wikidata_organization, wikidata_primary_source
    )
    load_function.assert_called_once_with([extracted_wikidata_organization])

    # transformation returns no organization
    mocked_search_organization_by_label.reset_mock()
    mocked_transform_wikidata_organization_to_extracted_organization.side_effect = None
    mocked_transform_wikidata_organization_to_extracted_organization.return_value = None
    mocked_transform_wikidata_organization_to_extracted_organization.reset_mock()
    load_function.reset_mock()
    _ORGANIZATION_BY_QUERY_CACHE.clear()
    returned = get_merged_organization_id_by_query_with_extract_transform_and_load(
        query_string, wikidata_primary_source, load_function
    )
    assert returned is None
    mocked_search_organization_by_label.assert_called_once_with(query_string)
    mocked_transform_wikidata_organization_to_extracted_organization.assert_called_once_with(
        wikidata_organization, wikidata_primary_source
    )
    load_function.assert_not_called()

    # search returns no organization
    mocked_search_organization_by_label.side_effect = None
    mocked_search_organization_by_label.return_value = None
    mocked_search_organization_by_label.reset_mock()
    mocked_transform_wikidata_organization_to_extracted_organization.reset_mock()
    load_function.reset_mock()
    _ORGANIZATION_BY_QUERY_CACHE.clear()
    returned = get_merged_organization_id_by_query_with_extract_transform_and_load(
        query_string, wikidata_primary_source, load_function
    )
    assert returned is None
    mocked_search_organization_by_label.assert_called_once_with(query_string)
    mocked_transform_wikidata_organization_to_extracted_organization.assert_not_called()
    load_function.assert_not_called()


@pytest.mark.integration()
def test_get_merged_organization_id_by_query_with_extract_transform_and_load(
    extracted_primary_sources: dict[str, ExtractedPrimarySource],
) -> None:
    wikidata_primary_source = extracted_primary_sources["wikidata"]
    returned = get_merged_organization_id_by_query_with_extract_transform_and_load(
        "Robert Koch-Institut", wikidata_primary_source, lambda _: None
    )
    assert returned == "ga6xh6pgMwgq7DC7r6Wjqg"
