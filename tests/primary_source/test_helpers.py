from mex.common.models import ExtractedPrimarySource
from mex.common.primary_source.helpers import (
    get_extracted_primary_source_by_name,
)


def test_get_extracted_primary_source_by_name() -> None:
    string_wiki = "wikidata"
    string_nonsense = "this should give no match"

    # primary source found
    extracted_primary_source = get_extracted_primary_source_by_name(string_wiki)

    assert isinstance(extracted_primary_source, ExtractedPrimarySource)
    assert extracted_primary_source.identifierInPrimarySource == "wikidata"

    assert get_extracted_primary_source_by_name(string_nonsense) is None
