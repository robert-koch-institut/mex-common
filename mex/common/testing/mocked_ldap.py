import json
import os
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock
from uuid import UUID

import pytest

from mex.common.ldap.connector import LDAPConnector
from mex.common.ldap.models import LDAPActor, LDAPFunctionalAccount, LDAPPerson
from mex.common.ldap.transform import (
    transform_ldap_functional_account_to_extracted_contact_point,
    transform_ldap_person_to_extracted_person,
)
from mex.common.models import (
    ExtractedContactPoint,
    ExtractedOrganization,
    ExtractedOrganizationalUnit,
    ExtractedPerson,
    PaginatedItemsContainer,
)
from mex.common.settings import BaseSettings
from mex.common.transform import MExEncoder, normalize
from mex.common.types import MergedPrimarySourceIdentifier


@pytest.fixture
def ldap_roland_resolved() -> LDAPPerson:
    """Return an LDAPPerson for Roland Resolved."""
    return LDAPPerson(
        sAMAccountName="ResolvedR",
        employeeID="42",
        sn="Resolved",
        givenName=["Roland"],
        displayName="Resolved, Roland",
        objectGUID=UUID(int=1, version=4),
        department="PARENT-UNIT",
        departmentNumber="FG99",
        mail=["resolvedr@rki.de"],
    )


@pytest.fixture
def roland_resolved(
    ldap_roland_resolved: LDAPPerson,
    mocked_units_by_identifier_in_primary_source: dict[
        str, ExtractedOrganizationalUnit
    ],
    extracted_organization_rki: ExtractedOrganization,
    extracted_primary_source_ids: dict[str, MergedPrimarySourceIdentifier],
) -> ExtractedPerson:
    """Return an ExtractedPerson for Roland Resolved."""
    return transform_ldap_person_to_extracted_person(
        ldap_roland_resolved,
        extracted_primary_source_ids["ldap"],
        mocked_units_by_identifier_in_primary_source,
        extracted_organization_rki.stableTargetId,
    )


@pytest.fixture
def ldap_juturna_felicitas() -> LDAPPerson:
    """Return an LDAPPerson for Juturna Felicitás."""
    return LDAPPerson(
        sAMAccountName="FelicitasJ",
        employeeID="70",
        sn="Felicitás",
        givenName=["Juturna"],
        displayName="Felicitás, Juturna",
        objectGUID=UUID(int=2, version=4),
        department="FG99",
        mail=["felicitasj@rki.de"],
    )


@pytest.fixture
def juturna_felicitas(
    ldap_juturna_felicitas: LDAPPerson,
    mocked_units_by_identifier_in_primary_source: dict[
        str, ExtractedOrganizationalUnit
    ],
    extracted_organization_rki: ExtractedOrganization,
    extracted_primary_source_ids: dict[str, MergedPrimarySourceIdentifier],
) -> ExtractedPerson:
    """Return an ExtractedPerson for Juturna Felicitás."""
    return transform_ldap_person_to_extracted_person(
        ldap_juturna_felicitas,
        extracted_primary_source_ids["ldap"],
        mocked_units_by_identifier_in_primary_source,
        extracted_organization_rki.stableTargetId,
    )


@pytest.fixture
def ldap_frieda_fictitious() -> LDAPPerson:
    """Return an LDAPPerson for Frieda Fictitious."""
    return LDAPPerson(
        sAMAccountName="FictitiousF",
        employeeID="71",
        sn="Fictitious",
        givenName=["Frieda"],
        displayName="Fictitious, Frieda, Dr.",
        objectGUID=UUID(int=3, version=4),
        department="FG99",
        mail=["fictitiousf@rki.de"],
    )


@pytest.fixture
def frieda_fictitious(
    ldap_frieda_fictitious: LDAPPerson,
    mocked_units_by_identifier_in_primary_source: dict[
        str, ExtractedOrganizationalUnit
    ],
    extracted_organization_rki: ExtractedOrganization,
    extracted_primary_source_ids: dict[str, MergedPrimarySourceIdentifier],
) -> ExtractedPerson:
    """Return an LDAPPerson for Frieda Fictitious."""
    return transform_ldap_person_to_extracted_person(
        ldap_frieda_fictitious,
        extracted_primary_source_ids["ldap"],
        mocked_units_by_identifier_in_primary_source,
        extracted_organization_rki.stableTargetId,
    )


@pytest.fixture
def ldap_contact_point() -> LDAPFunctionalAccount:
    """Return an LDAPFunctionalAccount for a dummy contact point."""
    return LDAPFunctionalAccount(
        sAMAccountName="ContactC",
        objectGUID=UUID(int=4, version=4),
        mail=["contactc@rki.de"],
        ou=["Funktion"],
    )


@pytest.fixture
def contact_point(
    ldap_contact_point: LDAPFunctionalAccount,
    extracted_primary_source_ids: dict[str, MergedPrimarySourceIdentifier],
) -> ExtractedContactPoint:
    """Return an ExtractedContactPoint for a dummy contact point."""
    return transform_ldap_functional_account_to_extracted_contact_point(
        ldap_contact_point,
        extracted_primary_source_ids["ldap"],
    )


def ldap_mock_searcher(actors: list[LDAPActor]) -> Callable[..., Any]:
    """Create a mocked search that picks the best match by simple token matching."""

    def tokenize(obj: object) -> set[str]:
        serialized = json.dumps(obj, cls=MExEncoder, ensure_ascii=False)
        return set(normalize(serialized.lower()).split())

    def mock_search(
        _self: LDAPConnector, **kwargs: dict[str, Any]
    ) -> PaginatedItemsContainer[LDAPActor]:
        tokenized_query = tokenize(kwargs)
        actors_by_score = [
            (len(tokenized_query & tokenize(actor)), actor) for actor in actors
        ]
        items = [i[1] for i in sorted(actors_by_score, key=lambda i: i[0])][-1:]
        return PaginatedItemsContainer[LDAPActor](items=items, total=len(items))

    return mock_search


@pytest.fixture(params=["ldap_patched_connector", "ldap_mock_server"])
def mocked_ldap(  # noqa: PLR0913
    request: pytest.FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
    ldap_contact_point: LDAPFunctionalAccount,
    ldap_roland_resolved: LDAPPerson,
    ldap_juturna_felicitas: LDAPPerson,
    ldap_frieda_fictitious: LDAPPerson,
) -> None:
    """Run each test with patched connector and/or against a mock server."""
    if request.param == "ldap_patched_connector":
        monkeypatch.setattr(
            LDAPConnector,
            "__init__",
            lambda self: setattr(self, "_connection", MagicMock()),
        )
        monkeypatch.setattr(
            LDAPConnector,
            "get_functional_accounts",
            ldap_mock_searcher(
                [ldap_contact_point],
            ),
        )
        monkeypatch.setattr(
            LDAPConnector,
            "get_persons",
            ldap_mock_searcher(
                [ldap_roland_resolved, ldap_juturna_felicitas, ldap_frieda_fictitious]
            ),
        )
    elif request.param == "ldap_mock_server":
        if "MEX_LDAP_SEARCH_BASE" not in os.environ:
            pytest.skip("Ldap mock server not configured")
        else:
            # the mock server uses a self-signed certificate, so disable TLS
            # verification to allow connecting to it during testing
            monkeypatch.setattr(BaseSettings.get(), "verify_session", False)
