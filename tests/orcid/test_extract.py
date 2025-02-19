import pytest
from requests import HTTPError

from mex.common.exceptions import EmptySearchResultError, FoundMoreThanOneError
from mex.common.orcid.extract import (
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
            '"Jayne Carberry"',
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
            pytest.raises(
                EmptySearchResultError,
            ),
        ),
        (
            "Multiple",
            "Doe",
            None,
            None,
            pytest.raises(
                FoundMoreThanOneError,
            ),
        ),
        (
            None,
            None,
            "Jayne Carberry",
            None,
            pytest.raises(
                FoundMoreThanOneError,
            ),
        ),
    ],
    ids=["existing", "existing_jayne", "not_existing", "multiple", "multiple_jayne"],
)
@pytest.mark.usefixtures("mocked_orcid")
def test_get_orcid_record_by_name(
    given_names, family_name, given_and_familyname, expected_result, error
):
    if error:
        with error:
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
    ("orcid_id", "expected_result", "error"),
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
        ),
        ("0000-0000-0000-0000", None, pytest.raises(HTTPError, match="404 Not Found")),
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
