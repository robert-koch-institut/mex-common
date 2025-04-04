import pytest
from requests import HTTPError

from mex.common.exceptions import EmptySearchResultError, FoundMoreThanOneError
from mex.common.orcid.extract import (
    get_orcid_record_by_id,
    get_orcid_record_by_name,
    search_records_by_name,
)
from mex.common.orcid.models import (
    OrcidEmails,
    OrcidFamilyName,
    OrcidGivenNames,
    OrcidIdentifier,
    OrcidName,
    OrcidPerson,
    OrcidRecord,
)


@pytest.mark.parametrize(
    ("given_names", "family_name", "given_and_familyname", "expected_result", "error"),
    [
        (
            "John",
            "Doe",
            None,
            OrcidRecord(
                orcid_identifier=OrcidIdentifier(
                    path="0009-0004-3041-5706",
                    uri="https://orcid.org/0009-0004-3041-5706",
                ),
                person=OrcidPerson(
                    emails=OrcidEmails(email=[]),
                    name=OrcidName(
                        family_name=OrcidFamilyName(value="Doe"),
                        given_names=OrcidGivenNames(value="John"),
                        visibility="public",
                    ),
                ),
            ),
            None,
        ),
        (
            None,
            None,
            "Jayne Carberry",
            OrcidRecord(
                orcid_identifier=OrcidIdentifier(
                    path="0000-0003-4634-4047",
                    uri="https://orcid.org/0000-0003-4634-4047",
                ),
                person=OrcidPerson(
                    emails=OrcidEmails(email=[]),
                    name=OrcidName(
                        family_name=OrcidFamilyName(value="Carberry"),
                        given_names=OrcidGivenNames(value="Jayne"),
                        visibility="public",
                    ),
                ),
            ),
            None,
        ),
        (
            "NotExistJohn",
            "Doe",
            None,
            None,
            EmptySearchResultError,
        ),
        (
            "Multiple",
            "Doe",
            None,
            None,
            FoundMoreThanOneError,
        ),
        (
            None,
            None,
            "Multiple Carberry",
            None,
            FoundMoreThanOneError,
        ),
    ],
    ids=["existing", "existing_jayne", "not_existing", "multiple", "multiple_jayne"],
)
@pytest.mark.usefixtures("mocked_orcid")
def test_get_orcid_record_by_name(
    given_names: str,
    family_name: str,
    given_and_familyname: str,
    expected_result: OrcidRecord,
    error: type[Exception],
) -> None:
    if error:
        with pytest.raises(error):
            get_orcid_record_by_name(
                given_names=given_names,
                family_name=family_name,
                given_and_family_names=given_and_familyname,
            )
    else:
        result = get_orcid_record_by_name(
            given_names=given_names,
            family_name=family_name,
            given_and_family_names=given_and_familyname,
        )
        assert result == expected_result


@pytest.mark.usefixtures("mocked_orcid")
@pytest.mark.parametrize(
    ("orcid_id", "expected_result", "error", "error_message"),
    [
        (
            "0009-0004-3041-5706",
            OrcidRecord(
                orcid_identifier=OrcidIdentifier(
                    path="0009-0004-3041-5706",
                    uri="https://orcid.org/0009-0004-3041-5706",
                ),
                person=OrcidPerson(
                    emails=OrcidEmails(email=[]),
                    name=OrcidName(
                        family_name=OrcidFamilyName(value="Doe"),
                        given_names=OrcidGivenNames(value="John"),
                        visibility="public",
                    ),
                ),
            ),
            None,
            None,
        ),
        ("0000-0000-0000-000", None, HTTPError, "404 Not Found"),
    ],
    ids=["existing id", "non-existing id"],
)
def test_get_orcid_record_by_id(
    orcid_id: str,
    expected_result: OrcidRecord,
    error: type[Exception],
    error_message: str,
) -> None:
    if error:
        with pytest.raises(HTTPError, match=error_message):
            get_orcid_record_by_id(orcid_id)
    else:
        result = get_orcid_record_by_id(orcid_id)
        assert result == expected_result


jayne_carberry_result = OrcidRecord(
    orcid_identifier=OrcidIdentifier(
        path="0000-0003-4634-4047", uri="https://orcid.org/0000-0003-4634-4047"
    ),
    person=OrcidPerson(
        emails=OrcidEmails(email=[]),
        name=OrcidName(
            family_name=OrcidFamilyName(value="Carberry"),
            given_names=OrcidGivenNames(value="Jayne"),
            visibility="public",
        ),
    ),
)


@pytest.mark.usefixtures("mocked_orcid")
@pytest.mark.parametrize(
    ("search_string", "expected_result"),
    [
        ("Jayne Carberry", [jayne_carberry_result]),
        ("Multiple Carberry", [jayne_carberry_result] * 10),
    ],
    ids=["single result", "multiple results"],
)
def test_get_orcid_records_by_given_or_family_name(
    search_string: str, expected_result: list[OrcidRecord]
) -> None:
    response = search_records_by_name(given_and_family_names=search_string)
    assert response.total == len(expected_result)
    assert response.items == expected_result
