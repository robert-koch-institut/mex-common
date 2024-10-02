from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch

from mex.common.models import ExtractedPrimarySource
from mex.common.primary_source import helpers
from mex.common.primary_source.helpers import (
    get_all_extracted_primary_sources,
    get_extracted_primary_source_by_name,
)


@pytest.mark.usefixtures("extracted_primary_sources")
def test_get_extracted_primary_source_by_name(
    monkeypatch: MonkeyPatch,
) -> None:
    query_string = "biospecimen"

    # mock all the things
    mocked_get_all_extracted_primary_sources = Mock(
        side_effect=get_all_extracted_primary_sources
    )
    monkeypatch.setattr(
        helpers,
        "get_all_extracted_primary_sources",
        mocked_get_all_extracted_primary_sources,
    )
    mocked_get_extracted_primary_source_by_name = Mock(
        side_effect=get_extracted_primary_source_by_name
    )
    monkeypatch.setattr(
        helpers,
        "get_extracted_primary_source_by_name",
        mocked_get_extracted_primary_source_by_name,
    )

    # primary source found
    extracted_primary_source = get_extracted_primary_source_by_name(query_string)

    assert isinstance(extracted_primary_source, ExtractedPrimarySource)
    assert extracted_primary_source.identifierInPrimarySource == "biospecimen"
    mocked_get_all_extracted_primary_sources.assert_called_once()
