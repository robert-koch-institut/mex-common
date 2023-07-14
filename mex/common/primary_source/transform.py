import json
from typing import Optional

from mex.common.models import ExtractedPrimarySource
from mex.common.primary_source.models import MExDBPrimarySource
from mex.common.types import Identifier, Link, Text

MEX_PRIMARY_SOURCE_ID = Identifier.generate(seed=0)


def transform_mex_db_primary_source_to_extracted_primary_source(
    mex_db_primary_source: MExDBPrimarySource,
    mex_db_mex_db_primary_source: Optional[ExtractedPrimarySource] = None,
    unit_merged_ids_by_synonym: dict[str, Identifier] = {},
) -> ExtractedPrimarySource:
    """Transform a concrete primary source coming from MEx DB into a primary source.

    Args:
        mex_db_primary_source: concrete MEx DB primary_source to transform
        mex_db_mex_db_primary_source: MEx DB primary source for the MEx DB primary_source itself
            (can be left empty if we are extracting the MEx DB primary source from itself.)
        unit_merged_ids_by_synonym: Dict of Organigram Units merged ids

    Returns:
        Primary source transformed from `mex_db_primary_source`
    """
    alternative_titles = [
        Text(
            value=json.loads(title.alternative_title).get("value"),
            language=json.loads(title.alternative_title).get("language"),
        )
        for title in mex_db_primary_source.alternative_titles
    ]
    titles = [
        Text(
            value=json.loads(title.title).get("value"),
            language=json.loads(title.title).get("language"),
        )
        for title in mex_db_primary_source.titles
    ]
    descriptions = [
        Text(
            value=json.loads(desc.description).get("value"),
            language=json.loads(desc.description).get("language"),
        )
        for desc in mex_db_primary_source.descriptions
    ]
    documentations = [
        Link(
            language=json.loads(docs.documentation).get("language"),
            title=json.loads(docs.documentation).get("title"),
            url=json.loads(docs.documentation).get("url"),
        )
        for docs in mex_db_primary_source.documentations
    ]
    located_ats = [
        Link(
            language=json.loads(located_at.located_at).get("language"),
            title=json.loads(located_at.located_at).get("title"),
            url=json.loads(located_at.located_at).get("url"),
        )
        for located_at in mex_db_primary_source.located_ats
    ]

    return ExtractedPrimarySource(
        identifierInPrimarySource=mex_db_primary_source.identifier,
        alternativeTitle=alternative_titles,
        description=descriptions,
        documentation=documentations,
        locatedAt=located_ats,
        title=titles,
        unitInCharge=[
            unit_id
            for unit in mex_db_primary_source.units_in_charge
            if (unit_id := unit_merged_ids_by_synonym.get(unit.unit_in_charge))
        ],
        version=mex_db_primary_source.version,
        hadPrimarySource=mex_db_mex_db_primary_source.stableTargetId
        if mex_db_mex_db_primary_source
        else MEX_PRIMARY_SOURCE_ID,
    )
