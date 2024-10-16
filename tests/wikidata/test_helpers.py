import pytest

from mex.common.exceptions import MExError
from mex.common.models import ExtractedPrimarySource
from mex.common.wikidata.helpers import get_extracted_organization_from_wikidata
from mex.common.wikidata.models.organization import WikidataOrganization
from mex.common.wikidata.transform import (
    transform_wikidata_organization_to_extracted_organization,
)


@pytest.mark.usefixtures("mocked_wikidata")
def test_get_extracted_organization_from_wikidata(
    wikidata_organization: WikidataOrganization,
    extracted_primary_sources: dict[str, ExtractedPrimarySource],
) -> None:
    wikidata_primary_source = extracted_primary_sources["wikidata"]
    extracted_wikidata_organization = (
        transform_wikidata_organization_to_extracted_organization(
            wikidata_organization, wikidata_primary_source
        )
    )

    # organization found and transformed
    returned = get_extracted_organization_from_wikidata("Robert Koch-Institut")
    assert returned == extracted_wikidata_organization


@pytest.mark.integration
def test_get_extracted_organization_from_wikidata_for_nonsensequery_and_exception() -> (
    None
):
    try:
        string_nonsense = "this schould give no match"
        returned = get_extracted_organization_from_wikidata(string_nonsense)

        assert returned is None

    except MExError:
        pytest.fail("Primary Source Wikidata not found")
