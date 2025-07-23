from collections.abc import Generator, Iterable, Sequence

from mex.common.models import ExtractedOrganization, ExtractedPrimarySource
from mex.common.types import Text, TextLanguage
from mex.common.wikidata.models import Aliases, Claim, Labels, WikidataOrganization


def transform_wikidata_organizations_to_extracted_organizations(
    wikidata_organizations: Iterable[WikidataOrganization],
    wikidata_primary_source: ExtractedPrimarySource,
) -> Generator[ExtractedOrganization, None, None]:
    """Transform wikidata organizations into ExtractedOrganizations.

    Wikidata organizations without labels are skipped.

    Args:
        wikidata_organizations: Iterable of wikidata organization to be transformed
        wikidata_primary_source: Extracted primary source for wikidata

    Returns:
        Generator of ExtractedOrganizations
    """
    for wikidata_organization in wikidata_organizations:
        if extracted_organization := (
            transform_wikidata_organization_to_extracted_organization(
                wikidata_organization, wikidata_primary_source
            )
        ):
            yield extracted_organization


def transform_wikidata_organization_to_extracted_organization(
    wikidata_organization: WikidataOrganization,
    wikidata_primary_source: ExtractedPrimarySource,
) -> ExtractedOrganization | None:
    """Transform one wikidata organization into ExtractedOrganizations.

    If no labels are found on the wikidata organization, `None` is returned instead.

    Args:
        wikidata_organization: wikidata organization to be transformed
        wikidata_primary_source: Extracted primary source for wikidata

    Returns:
        ExtractedOrganization or None
    """
    labels = get_official_name_label(wikidata_organization.labels)
    if not labels:
        return None
    return ExtractedOrganization(
        wikidataId=f"http://www.wikidata.org/entity/{wikidata_organization.identifier}",
        officialName=labels,
        shortName=_get_clean_short_names(wikidata_organization.claims.short_name),
        geprisId=[],
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
        hadPrimarySource=wikidata_primary_source.stableTargetId,
        alternativeName=_get_alternative_names(
            wikidata_organization.claims.native_label, wikidata_organization.aliases
        ),
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


def get_official_name_label(labels: Labels) -> Text | None:
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
