from collections.abc import Generator, Iterable, Sequence

from mex.common.models import ExtractedLocation, ExtractedOrganization
from mex.common.types import MergedPrimarySourceIdentifier, Text, TextLanguage
from mex.common.wikidata.models import (
    Aliases,
    Claim,
    Labels,
    WikidataLocation,
    WikidataOrganization,
)


def transform_wikidata_organizations_to_extracted_organizations(
    wikidata_organizations: Iterable[WikidataOrganization],
    wikidata_primary_source_id: MergedPrimarySourceIdentifier,
) -> Generator[ExtractedOrganization, None, None]:
    """Transform wikidata organizations into ExtractedOrganizations.

    Wikidata organizations without labels are skipped.

    Args:
        wikidata_organizations: Iterable of wikidata organization to be transformed
        wikidata_primary_source_id: Extracted primary source id for wikidata

    Returns:
        Generator of ExtractedOrganizations
    """
    for wikidata_organization in wikidata_organizations:
        if extracted_organization := (
            transform_wikidata_organization_to_extracted_organization(
                wikidata_organization, wikidata_primary_source_id
            )
        ):
            yield extracted_organization


def transform_wikidata_organization_to_extracted_organization(
    wikidata_organization: WikidataOrganization,
    wikidata_primary_source_id: MergedPrimarySourceIdentifier,
) -> ExtractedOrganization | None:
    """Transform one wikidata organization into an ExtractedOrganization.

    If no labels are found on the wikidata organization, `None` is returned instead.

    Args:
        wikidata_organization: wikidata organization to be transformed
        wikidata_primary_source_id: Extracted primary source id for wikidata

    Returns:
        ExtractedOrganization or None
    """
    label = _get_preferred_label(wikidata_organization.labels)
    if not label:
        return None
    return ExtractedOrganization(
        wikidataId=_get_wikidata_entity_url(wikidata_organization.identifier),
        officialName=label,
        shortName=_get_clean_short_names(wikidata_organization.claims.short_name),
        geprisId=[
            f"https://gepris.dfg.de/gepris/institution/{value}"
            for claim in wikidata_organization.claims.gepris_id
            if (value := claim.mainsnak.datavalue.value.text)
        ],
        isniId=[
            f"https://isni.org/isni/{claim.mainsnak.datavalue.value.text}".replace(
                " ", ""
            )
            for claim in wikidata_organization.claims.isni_id
        ],
        gndId=[
            f"https://d-nb.info/gnd/{claim.mainsnak.datavalue.value.text}"
            for claim in wikidata_organization.claims.gnd_id
        ],
        viafId=[
            f"https://viaf.org/viaf/{claim.mainsnak.datavalue.value.text}"
            for claim in wikidata_organization.claims.viaf_id
        ],
        rorId=[
            f"https://ror.org/{claim.mainsnak.datavalue.value.text}"
            for claim in wikidata_organization.claims.ror_id
        ],
        identifierInPrimarySource=wikidata_organization.identifier,
        hadPrimarySource=wikidata_primary_source_id,
        alternativeName=_get_alternative_names(
            wikidata_organization.claims.native_label, wikidata_organization.aliases
        ),
    )


def transform_wikidata_locations_to_extracted_locations(
    wikidata_locations: Iterable[WikidataLocation],
    wikidata_primary_source_id: MergedPrimarySourceIdentifier,
) -> Generator[ExtractedLocation, None, None]:
    """Transform Wikidata locations into ExtractedLocations.

    Wikidata locations without labels are skipped.

    Args:
        wikidata_locations: Iterable of wikidata location to be transformed
        wikidata_primary_source_id: Extracted primary source id for wikidata

    Returns:
        Generator of ExtractedLocation
    """
    for wikidata_location in wikidata_locations:
        if extracted_location := (
            transform_wikidata_location_to_extracted_location(
                wikidata_location, wikidata_primary_source_id
            )
        ):
            yield extracted_location


def transform_wikidata_location_to_extracted_location(
    wikidata_location: WikidataLocation,
    wikidata_primary_source_id: MergedPrimarySourceIdentifier,
) -> ExtractedLocation | None:
    """Transform one wikidata location into an ExtractedLocation.

    If no labels are found on the wikidata location, `None` is returned instead.

    Args:
        wikidata_location: wikidata location to be transformed
        wikidata_primary_source_id: Extracted primary source id for wikidata

    Returns:
        ExtractedLocation or None
    """
    label = _get_preferred_label(wikidata_location.labels)
    if not label:
        return None
    return ExtractedLocation(
        wikidataId=_get_wikidata_entity_url(wikidata_location.identifier),
        name=label,
        geoNamesId=[
            f"http://www.geonames.org/{value}"
            for claim in wikidata_location.claims.geonames_id
            if (value := claim.mainsnak.datavalue.value.text)
        ],
        identifierInPrimarySource=wikidata_location.identifier,
        hadPrimarySource=wikidata_primary_source_id,
    )


def _get_alternative_names(
    native_labels: Sequence[Claim],
    all_aliases: Aliases,
) -> list[Text]:
    """Get alternative names of an organization in DE and EN.

    Args:
        native_labels: Sequence of all native labels
        all_aliases: All aliases of the organization

    Returns:
        combined list of native labels and aliases in DE and EN
    """
    alternative_names = []

    for alias in all_aliases.en + all_aliases.de:
        text = Text(value=alias.value, language=None)
        if text not in alternative_names:
            alternative_names.append(text)

    for native_label in native_labels:
        value = native_label.mainsnak.datavalue.value.text
        language = native_label.mainsnak.datavalue.value.language

        if not value:
            continue

        if language == "de":
            text = Text(value=value, language=TextLanguage.DE)
        elif language == "en":
            text = Text(value=value, language=TextLanguage.EN)
        else:
            continue

        if text not in alternative_names:
            alternative_names.append(text)

    return alternative_names


def _get_clean_short_names(short_names: Sequence[Claim]) -> list[Text]:
    """Get clean short names only in EN and DE and ignore the rest.

    Args:
        short_names: List of all short names

    Returns:
        list of clean short names in EN and DE
    """
    clean_short_names = []
    for short_name in short_names:
        value = short_name.mainsnak.datavalue.value.text
        language = short_name.mainsnak.datavalue.value.language

        if not value:
            continue

        if language == "de":
            text = Text(value=value, language=TextLanguage.DE)
        elif language == "en":
            text = Text(value=value, language=TextLanguage.EN)
        else:
            continue

        if text not in clean_short_names:
            clean_short_names.append(text)

    return clean_short_names


def _get_preferred_label(labels: Labels) -> Text | None:
    """Get if DE label is available and return a list of EN and DE labels.

    Args:
        labels: Wikidata labels object

    Returns:
        Text object of the label that was picked, or None
    """
    if labels.de:
        return Text(value=labels.de.value, language=TextLanguage.DE)
    if labels.en:
        return Text(value=labels.en.value, language=TextLanguage.EN)
    if labels.multiple:
        return Text(value=labels.multiple.value, language=None)
    return None


def _get_wikidata_entity_url(identifier: str) -> str:
    return f"http://www.wikidata.org/entity/{identifier}"
