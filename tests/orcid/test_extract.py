import pytest

from mex.common.exceptions import EmptySearchResultError, FoundMoreThanOneError
from mex.common.orcid.extract import get_person_by_id, get_person_by_name
from tests.orcid.conftest import EXPECTED_JOHN


@pytest.mark.parametrize(
    ("family_name", "given_names", "error"),
    [
        (
            "Mustermann",
            "Max",
            pytest.raises(
                FoundMoreThanOneError,
                match="Found multiple AD persons for filters {'given-names': 'Max', 'family-name': 'Mustermann'}",
            ),
        ),
        (
            "Defgh",
            "Abc",
            pytest.raises(
                EmptySearchResultError,
                match="Cannot find orcid person for filters {'given-names': 'Abc', 'family-name': 'Defgh'}",
            ),
        ),
    ],
    ids=["multiple results", "empty result"],
)
def test_search_errors(family_name, given_names, error):
    with error:
        get_person_by_name(given_names=given_names, family_name=family_name)


@pytest.mark.parametrize(
    ("string_id", "expected"),
    [
        ("0000-0002-1825-0097", EXPECTED_JOHN),
        ("0009-0004-3041-576", {"result": None, "num-found": 0}),
        ("invalid-orcid-id", {"result": None, "num-found": 0}),
    ],
    ids=["existing person", "non-existing person", "invalid characters"],
)
def test_get_person_details_by_orcid_id(string_id, expected) -> None:
    result = get_person_by_id(orcid_id=string_id)
    if result.get("num-found"):
        assert result.get("num-found") == expected.get("num-found")
    assert result == expected
