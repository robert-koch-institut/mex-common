from collections.abc import Generator
from functools import cache
from typing import TypeVar
from urllib.parse import urlsplit

from ldap3 import AUTO_BIND_NO_TLS, Connection, Server
from ldap3.core.exceptions import LDAPExceptionError

from mex.common.connector import BaseConnector
from mex.common.exceptions import (
    EmptySearchResultError,
    FoundMoreThanOneError,
    MExError,
)
from mex.common.ldap.models.actor import LDAPActor
from mex.common.ldap.models.person import LDAPPerson
from mex.common.ldap.models.unit import LDAPUnit
from mex.common.settings import BaseSettings

ModelT = TypeVar("ModelT", bound=LDAPActor)


class LDAPConnector(BaseConnector):
    """Connector class to handle credentials and querying of LDAP."""

    DEFAULT_PORT = 636
    SEARCH_BASE = "DC=rki,DC=local"
    PAGE_SIZE = 25

    def __init__(self) -> None:
        """Create a new LDAP connection."""
        settings = BaseSettings.get()
        url = urlsplit(settings.ldap_url.get_secret_value())
        host = str(url.hostname)
        port = int(url.port or self.DEFAULT_PORT)
        server = Server(host, port, use_ssl=True)
        connection = Connection(
            server,
            user=url.username,
            password=url.password,
            auto_bind=AUTO_BIND_NO_TLS,
            read_only=True,
        )
        self._connection = connection.__enter__()
        if not self._is_service_available():
            raise MExError(f"LDAP service not available at url: {host}:{port}")

    def _is_service_available(self) -> bool:
        try:
            return self._connection.server.check_availability() is True
        except LDAPExceptionError:
            return False

    def close(self) -> None:
        """Close the connector's underlying LDAP connection."""
        self._connection.__exit__(None, None, None)

    def _fetch(
        self, model_cls: type[ModelT], /, **filters: str
    ) -> Generator[ModelT, None, None]:
        """Fetch all items that match the given filters and parse to given model.

        Args:
            model_cls: Pydantic model class
            **filters: LDAP compatible filters, will be joined in AND-condition

        Returns:
            Generator for instance of `model_cls`
        """
        search_filter = "".join(f"({key}={value})" for key, value in filters.items())
        entries = self._paged_ldap_search(
            model_cls.get_ldap_fields(), search_filter, self.SEARCH_BASE
        )
        for entry in entries:
            if attributes := entry.get("attributes"):
                yield model_cls.model_validate(attributes)

    @cache  # noqa: B019
    def _paged_ldap_search(
        self, fields: tuple[str], search_filter: str, search_base: str
    ) -> list[dict[str, str]]:
        entries = self._connection.extend.standard.paged_search(
            search_base=search_base,
            search_filter=f"(&{search_filter})",
            attributes=fields,
        )
        return list(entries)

    def get_functional_accounts(
        self, mail: str = "*", sAMAccountName: str = "*", **filters: str  # noqa: N803
    ) -> Generator[LDAPActor, None, None]:
        """Get LDAP functional accounts that match provided filters.

        Some projects/resources declare functional mailboxes as their contact.

        Args:
            mail: Email address of the functional account
            sAMAccountName: Account name
            **filters: Additional filters

        Returns:
            Generator for LDAP functional accounts
        """
        yield from self._fetch(
            LDAPUnit,
            objectCategory="Person",
            OU="Funktion",
            sAMAccountName=sAMAccountName,
            mail=mail,
            **filters,
        )

    def get_persons(
        self, surname: str = "*", given_name: str = "*", mail: str = "*", **filters: str
    ) -> Generator[LDAPPerson, None, None]:
        """Get LDAP persons that match the provided filters.

        An LDAP person's objectGUIDs is stable across name changes, whereas name based
        person identifiers of the schema SurnameF are not stable.

        Only consider LDAP entries of objectClass 'user', ObjectCategory 'Person'.
        Additional required attributes are: sAMAccountName, employeeId.

        Args:
            given_name: Given name of a person, defaults to non-null
            surname: Surname of a person, defaults to non-null
            mail: Email address, defaults to non-null
            **filters: Additional filters

        Returns:
            Generator for LDAP persons
        """
        yield from self._fetch(
            LDAPPerson,
            objectClass="user",
            objectCategory="Person",
            sAMAccountName="*",
            employeeId="*",
            mail=mail,
            sn=surname,
            givenName=given_name,
            **filters,
        )

    def get_units(
        self, sAMAccountName: str = "*", mail: str = "*", **filters: str  # noqa: N803
    ) -> Generator[LDAPUnit, None, None]:
        """Get LDAP units that match the provided filters.

        Args:
            sAMAccountName: Account name of the unit
            mail: Email address of the unit
            **filters: Additional filters

        Returns:
            Generator for LDAP units
        """
        yield from self._fetch(
            LDAPUnit,
            OU="Funktion",
            sAMAccountName=sAMAccountName,
            mail=mail,
            **filters,
        )

    def get_functional_account(
        self, objectGUID: str = "*", **filters: str  # noqa: N803
    ) -> LDAPActor:
        """Get a single LDAP functional account for the given filters.

        Args:
            objectGUID: Internal LDAP identifier
            **filters: Filters for LDAP search

        Raises:
            MExError: If number of LDAP entries that match the filters is not 1

        Returns:
            Single LDAP functional account matching the filters
        """
        functional_accounts = list(
            self.get_functional_accounts(
                objectGUID=objectGUID,
                **filters,
            )
        )
        if not functional_accounts:
            raise EmptySearchResultError(
                "Cannot find AD functional account for filters "
                f"'objectGUID: {objectGUID}, {filters}'"
            )
        if len(functional_accounts) > 1:
            raise FoundMoreThanOneError(
                "Found multiple AD functional accounts for filters "
                f"'objectGUID: {objectGUID}, {filters}'"
            )
        return functional_accounts[0]

    def get_person(
        self, objectGUID: str = "*", employeeID: str = "*", **filters: str  # noqa: N803
    ) -> LDAPPerson:
        """Get a single LDAP person for the given filters.

        Args:
            objectGUID: Internal LDAP identifier
            employeeID: Employee ID, must be present
            **filters: Filters for LDAP search

        Raises:
            MExError: If number of LDAP entries that match the filters is not 1

        Returns:
            Single LDAP person matching the filters
        """
        persons = list(
            self.get_persons(
                objectGUID=objectGUID,
                employeeID=employeeID,
                **filters,
            )
        )
        if not persons:
            raise EmptySearchResultError(
                f"Cannot find AD person for filters 'objectGUID: {objectGUID}, "
                f"employeeID: {employeeID}, {filters}'"
            )
        if len(persons) > 1:
            raise FoundMoreThanOneError(
                f"Found multiple AD persons for filters 'objectGUID: {objectGUID}, "
                f"employeeID: {employeeID}, {filters}'"
            )
        return persons[0]

    def get_unit(self, **filters: str) -> LDAPUnit:
        """Get a single LDAP unit for the given filters.

        Args:
            **filters: Filters for LDAP search

        Raises:
            MExError: If number of LDAP entries that match the filters is not 1

        Returns:
            Single LDAP unit matching the filters
        """
        units = list(self.get_units(**filters))
        if not units:
            raise EmptySearchResultError(f"Cannot find AD unit for filters '{filters}'")
        if len(units) > 1:
            raise FoundMoreThanOneError(
                f"Found multiple AD units for filters '{filters}'"
            )
        return units[0]
