from typing import TYPE_CHECKING

from mex.common.primary_source.helpers import (
    get_extracted_primary_source_by_name,
)
from mex.common.wikidata.extract import (
    get_wikidata_location,
    get_wikidata_organization,
)
from mex.common.wikidata.models import WikidataOrganizationResult
from mex.common.wikidata.transform import (
    transform_wikidata_location_to_extracted_location,
    transform_wikidata_organization_to_extracted_organization,
)

if TYPE_CHECKING:
    from mex.common.models import ExtractedLocation

WIKIDATA_PRIMARY_SOURCE_NAME = "wikidata"


def get_wikidata_organization_with_locations(
    wikidata_id: str,
) -> WikidataOrganizationResult | None:
    """Get an organization and its country locations from Wikidata."""
    primary_source = get_extracted_primary_source_by_name(WIKIDATA_PRIMARY_SOURCE_NAME)
    if primary_source is None:
        msg = "Wikidata primary source not found."
        raise ValueError(msg)

    wikidata_organization = get_wikidata_organization(wikidata_id)

    country_qids = {
        claim.mainsnak.datavalue.value.id
        for claim in wikidata_organization.claims.country_id
        if claim.mainsnak.datavalue.value.id is not None
    }

    extracted_locations: set[ExtractedLocation] = set()

    for qid in country_qids:
        wikidata_location = get_wikidata_location(qid)

        extracted_location = transform_wikidata_location_to_extracted_location(
            wikidata_location,
            primary_source.stableTargetId,
        )

        if extracted_location is not None:
            extracted_locations.add(extracted_location)

    extracted_organization = transform_wikidata_organization_to_extracted_organization(
        wikidata_organization,
        primary_source.stableTargetId,
        country=[location.stableTargetId for location in extracted_locations],
    )

    if extracted_organization is None:
        return None

    return WikidataOrganizationResult(
        organization=extracted_organization,
        locations=list(extracted_locations),
        primary_source=primary_source,
    )
