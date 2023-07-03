from typing import Any, Callable
from unittest.mock import MagicMock, Mock

import pytest
from ldap3 import Connection
from pytest import MonkeyPatch

from mex.common.ldap.connector import LDAPConnector
from mex.common.models.primary_source import ExtractedPrimarySource
from mex.common.primary_source.extract import extract_mex_db_primary_source_by_id
from mex.common.primary_source.transform import (
    transform_mex_db_primary_source_to_extracted_primary_source,
)
from mex.common.settings import BaseSettings
from mex.common.testing import insert_test_primary_sources_into_db

PagedSearchResults = list[list[dict[str, Any]]]
LDAPMocker = Callable[[PagedSearchResults], None]


SAMPLE_PERSON_ATTRS = dict(
    company=["RKI"],
    department=["XY"],
    departmentNumber=["XY2"],
    displayName=["Sample, Sam"],
    employeeID=["1024"],
    givenName=["Sam"],
    mail=["SampleS@mail.tld"],
    objectGUID=["{00000000-0000-4000-8000-000000000000}"],
    ou=["XY"],
    sAMAccountName=["SampleS"],
    sn=["Sample"],
)

XY_DEPARTMENT_ATTRS = dict(
    mail=["XY@mail.tld"],
    objectGUID=["{00000000-0000-4000-8000-000000000042}"],
    sAMAccountName=["XY"],
)

XY2_DEPARTMENT_ATTRS = dict(
    mail=["XY2@mail.tld"],
    objectGUID=["{00000000-0000-4000-8000-000000000043}"],
    sAMAccountName=["XY2"],
)


@pytest.fixture(autouse=True)
def seed_primary_sources_into_db() -> None:
    """Seed mex-db and ldap primary sourcea data into temp database."""
    insert_test_primary_sources_into_db("mex-db", "ldap")


@pytest.fixture
def extracted_primary_source() -> ExtractedPrimarySource:
    """Return an extracted primary source for the ldap primary source."""
    mex_db_primary_source = extract_mex_db_primary_source_by_id("ldap")
    return transform_mex_db_primary_source_to_extracted_primary_source(
        mex_db_primary_source
    )


@pytest.fixture
def ldap_mocker(monkeypatch: MonkeyPatch) -> LDAPMocker:
    """Patch the LDAP connector to return `SAMPLE_PERSON_ATTRS` from its connection."""

    def mocker(results: PagedSearchResults) -> None:
        def __init__(self: LDAPConnector, settings: BaseSettings) -> None:
            self.connection = MagicMock(spec=Connection, extend=Mock())
            self.connection.extend.standard.paged_search = MagicMock(
                side_effect=[
                    [dict(attributes=e) for e in entries] for entries in results
                ]
            )

        monkeypatch.setattr(LDAPConnector, "__init__", __init__)

    return mocker
