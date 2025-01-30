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
    ("given_names", "family_name", "expected_result", "error"),
    [
        (
            "John",
            "Doe",
            OrcidRecord(
                orcid_identifier=OrcidIdentifier(
                    path="0000-0002-1825-0097",
                    uri="https://orcid.org/0000-0002-1825-0097",
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
            "NotExistJohn",
            "Doe",
            None,
            pytest.raises(
                EmptySearchResultError,
            ),
        ),
        (
            "Multiple",
            "Doe",
            None,
            pytest.raises(
                FoundMoreThanOneError,
            ),
        ),
    ],
    ids=[],
)
@pytest.mark.usefixtures("mocked_orcid")
def test_get_orcid_record_by_name(given_names, family_name, expected_result, error):
    if error:
        with error:
            get_orcid_record_by_name(given_names, family_name)
    else:
        result = get_orcid_record_by_name(given_names, family_name)
        assert result == expected_result


@pytest.mark.usefixtures("mocked_orcid")
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
