from typing import Generator, Iterable

from mex.common.models import ExtractedOrganization, ExtractedPrimarySource
from mex.common.types import Text, TextLanguage
from mex.common.wikidata.models.organization import (
    Aliases,
    Claim,
    Labels,
    WikidataOrganization,
)


def transform_wikidata_organizations_to_extracted_organizations(
    wikidata_organizations: Iterable[WikidataOrganization],
    extracted_primary_source_wikidata: ExtractedPrimarySource,
) -> Generator[ExtractedOrganization, None, None]:
    """Transform wikidata organizations into ExtractedOrganizations.

    Args:
        wikidata_organizations: Iterable of wikidata organization to be transformed
        wikidata_primary_source: Extracted primary source for wikidata

    Returns:
        Generator of ExtractedOrganizations
    """
    for organization in wikidata_organizations:
        labels = get_clean_labels(organization.labels)
        if not labels:
            continue
        yield ExtractedOrganization(
            wikidataId=f"https://www.wikidata.org/entity/{organization.identifier}",
            officialName=labels,
            shortName=get_clean_short_names(organization.claims.short_name),
            isniId=[
                f"https://isni.org/isni/{claim.mainsnak.datavalue.value.text}".replace(
                    " ", ""
                )
                for claim in organization.claims.isni_id
            ],
            gndId=[
                f"https://d-nb.info/gnd/{claim.mainsnak.datavalue.value.text}"
                for claim in organization.claims.gnd_id
            ],
            viafId=[
                f"https://viaf.org/viaf/{claim.mainsnak.datavalue.value.text}"
                for claim in organization.claims.viaf_id
            ],
            rorId=[
                f"https://ror.org/{claim.mainsnak.datavalue.value.text}"
                for claim in organization.claims.ror_id
            ],
            identifierInPrimarySource=organization.identifier,
            hadPrimarySource=extracted_primary_source_wikidata.identifier,
            alternativeName=get_alternative_names(
                organization.claims.native_label, organization.aliases
            ),
        )


def get_alternative_names(
    native_labels: list[Claim], all_aliases: Aliases
) -> list[Text]:
    """Get alternative names of an organization in DE and EN.

    Args:
        native_labels (list[Claim]): List of all native labels
        all_aliases (Aliases): All aliases of the organization

    Returns:
        combined list of native labels and aliases in DE and EN
    """
    alternative_names = []
    for alias in all_aliases.en + all_aliases.de:
        alternative_names.append(Text(value=alias.value, language=None))

    for native_label in native_labels:
        value = native_label.mainsnak.datavalue.value.text
        language = native_label.mainsnak.datavalue.value.language

        if not value:
            continue

        if language == "de":
            alternative_names.append(Text(value=value, language=TextLanguage.DE))
        elif language == "en":
            alternative_names.append(Text(value=value, language=TextLanguage.EN))

    return list(set(alternative_names))


def get_clean_short_names(short_names: list[Claim]) -> list[Text]:
    """Get clean short names only in EN and DE and ignore the rest.

    Args:
        short_names: List of all short names

    Returns:
        list of clean short names in EN and DE
    """
    clean_short_name = []
    for short_name in short_names:
        value = short_name.mainsnak.datavalue.value.text
        language = short_name.mainsnak.datavalue.value.language

        if not value:
            continue

        if language == "de":
            clean_short_name.append(Text(value=value, language=TextLanguage.DE))
        elif language == "en":
            clean_short_name.append(Text(value=value, language=TextLanguage.EN))
    return list(set(clean_short_name))


def get_clean_labels(labels: Labels) -> list[Text]:
    """Check if DE label is available and return a list of EN and DE labels.

    Args:
        labels: labels object

    Returns:
        list of clean labels in EN and DE
    """
    clean_labels = []
    if labels.en:
        clean_labels.append(Text(value=labels.en.value, language=TextLanguage.EN))
    if labels.de:
        clean_labels.append(Text(value=labels.de.value, language=TextLanguage.DE))

    return clean_labels
