import pytest

from mex.common.exceptions import EmptySearchResultError, FoundMoreThanOneError
from mex.common.orcid.extract import (
    get_data_by_id,
    get_data_by_name,
    get_orcid_person_by_id,
    get_orcid_person_by_name,
)
from mex.common.orcid.models.person import FamilyName, GivenNames, OrcidPerson
from tests.orcid.conftest import DUMMYDATA_JOHN, DUMMYDATA_VYVY


def test_get_data_by_name():
    given_names = "Vyvy "
    family_name = "Tran Ngoc"
    expected_result = DUMMYDATA_VYVY
    result = get_data_by_name(given_names=given_names, family_name=family_name)
    assert expected_result == result


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
        get_data_by_name(given_names=given_names, family_name=family_name)


@pytest.mark.parametrize(
    ("string_id", "expected"),
    [
        (
            "0009-0004-3041-5706",
            DUMMYDATA_JOHN,
        ),
        ("0009-0004-3041-576", {"result": None, "num-found": 0}),
        ("invalid-orcid-id", {"result": None, "num-found": 0}),
    ],
    ids=["existing person", "non-existing person", "invalid characters"],
)
def test_get_data_by_orcid_id(string_id, expected) -> None:
    result = get_data_by_id(orcid_id=string_id)
    if result.get("num-found"):
        assert result.get("num-found") == expected.get("num-found")
    assert result == expected


@pytest.mark.parametrize(
    ("given_names", "family_name", "expected_result"),
    [
        (
            "Vyvy",
            "Tran Ngoc",
            OrcidPerson(
                orcid_identifier="0009-0004-3041-5706",
                email=[],
                given_names=GivenNames(given_names="VyVy", visibility="public"),
                family_name=FamilyName(family_name="Tran Ngoc", visibility="public"),
            ),
        )
    ],
)
def test_get_orcid_person_by_name(
    given_names,
    family_name,
    expected_result,
):
    result = get_orcid_person_by_name(given_names, family_name)
    assert result == expected_result


@pytest.mark.parametrize(
    ("orcid_id", "expected_result"),
    [
        (
            "0000-0002-1825-0097",
            OrcidPerson(
                orcid_identifier="0000-0002-1825-0097",
                email=[],
                given_names=GivenNames(given_names="Josiah", visibility="public"),
                family_name=FamilyName(family_name="Carberry", visibility="public"),
            ),
        ),
    ],
)
def test_get_orcid_person_by_id(
    orcid_id,
    expected_result,
):
    result = get_orcid_person_by_id(orcid_id)
    assert result == expected_result
