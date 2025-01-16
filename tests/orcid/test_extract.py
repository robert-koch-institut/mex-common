import pytest
from requests import HTTPError

from mex.common.exceptions import EmptySearchResultError, FoundMoreThanOneError
from mex.common.orcid.connector import get_data_by_id
from mex.common.orcid.extract import (
    get_data_by_name,
    get_orcid_record_by_id,
    get_orcid_record_by_name,
)
from mex.common.orcid.models.person import (
    OrcidEmails,
    OrcidFamilyName,
    OrcidGivenNames,
    OrcidIdentifier,
    OrcidName,
    OrcidPerson,
    OrcidRecord,
)
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
            pytest.raises(FoundMoreThanOneError),
        ),
        (
            "Defgh",
            "Abc",
            pytest.raises(EmptySearchResultError),
        ),
    ],
    ids=["multiple results", "empty result"],
)
def test_search_errors(family_name, given_names, error):
    with error:
        get_data_by_name(given_names=given_names, family_name=family_name)


@pytest.mark.parametrize(
    ("string_id", "expected", "error"),
    [
        ("0009-0004-3041-5706", DUMMYDATA_JOHN, None),
        ("0009-0004-3041-576", None, pytest.raises(HTTPError)),
        ("invalid-orcid-id", None, pytest.raises(HTTPError)),
    ],
    ids=["existing person", "non-existing person", "invalid characters"],
)
def test_get_data_by_orcid_id(string_id, expected, error) -> None:
    if error:
        with error:
            get_data_by_id(orcid_id=string_id)
    else:
        result = get_data_by_id(orcid_id=string_id)
        assert result == expected


@pytest.mark.parametrize(
    ("given_names", "family_name", "expected_result", "error"),
    [
        (
            "Vyvy",
            "Tran Ngoc",
            OrcidRecord(
                orcid_identifier=OrcidIdentifier(
                    path="0009-0004-3041-5706",
                    uri="https://orcid.org/0009-0004-3041-5706",
                ),
                person=OrcidPerson(
                    emails=OrcidEmails(email=[]),
                    name=OrcidName(
                        family_name=OrcidFamilyName(value="Tran Ngoc"),
                        given_names=OrcidGivenNames(value="VyVy"),
                        visibility="public",
                    ),
                ),
            ),
            None,
        ),
        (
            "Abc",
            "Defgh",
            None,
            pytest.raises(
                EmptySearchResultError,
            ),
        ),
        (
            "John",
            "Doe",
            None,
            pytest.raises(
                FoundMoreThanOneError,
            ),
        ),
    ],
    ids=[],
)
def test_get_orcid_record_by_name(given_names, family_name, expected_result, error):
    if error:
        with error:
            get_orcid_record_by_name(given_names, family_name)
    else:
        result = get_orcid_record_by_name(given_names, family_name)
        assert result == expected_result


@pytest.mark.parametrize(
    ("orcid_id", "expected_result", "error"),
    [
        (
            "0000-0002-1825-0097",
            OrcidRecord(
                orcid_identifier=OrcidIdentifier(
                    path="0000-0002-1825-0097",
                    uri="https://orcid.org/0000-0002-1825-0097",
                ),
                person=OrcidPerson(
                    emails=OrcidEmails(email=[]),
                    name=OrcidName(
                        family_name=OrcidFamilyName(value="Carberry"),
                        given_names=OrcidGivenNames(value="Josiah"),
                        visibility="public",
                    ),
                ),
            ),
            None,
        ),
        (
            "0000-0001-2345-6789",
            None,
            pytest.raises(HTTPError),
        ),
    ],
    ids=["existing id", "non-existing id"],
)
def test_get_orcid_record_by_id(orcid_id, expected_result, error):
    if error:
        with error:
            get_orcid_record_by_id(orcid_id)
    else:
        result = get_orcid_record_by_id(orcid_id)
        assert result == expected_result
