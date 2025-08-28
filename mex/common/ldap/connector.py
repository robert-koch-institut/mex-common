from typing import Any, cast
from urllib.parse import urlsplit

import backoff
from ldap3 import AUTO_BIND_NO_TLS, Connection, Server
from ldap3.core.exceptions import LDAPExceptionError, LDAPSocketSendError

from mex.common.connector import BaseConnector
from mex.common.exceptions import (
    EmptySearchResultError,
    FoundMoreThanOneError,
    MExError,
)
from mex.common.ldap.models import (
    AnyLDAPActor,
    LDAPActorTypeAdapter,
    LDAPFunctionalAccount,
    LDAPPerson,
)
from mex.common.logging import logger
from mex.common.settings import BaseSettings


class LDAPConnector(BaseConnector):
    """Connector class to handle credentials and querying of LDAP."""

    def __init__(self) -> None:
        """Create a new LDAP connection."""
        settings = BaseSettings.get()
        self._search_base = settings.ldap_search_base
        self._connection = self._setup_connection()

    def _setup_connection(self) -> Connection:
        """Set up a new LDAP connection."""
        settings = BaseSettings.get()
        url = urlsplit(settings.ldap_url.get_secret_value())
        host = str(url.hostname)
        port = int(url.port) if url.port else None
        server = Server(host, port, use_ssl=True)
        connection = Connection(
            server,
            user=url.username,
            password=url.password,
            auto_bind=AUTO_BIND_NO_TLS,
            read_only=True,
        )
        connection.__enter__()
        try:
            connection.server.check_availability()
        except LDAPExceptionError as error:
            msg = f"LDAP service not available at url: {host}:{port}"
            raise MExError(msg) from error
        return connection

    def close(self) -> None:
        """Close the connector's underlying LDAP connection."""
        if self._connection:
            self._connection.__exit__(None, None, None)

    def reconnect(self) -> None:
        """Close current ldap connection and initiate a new one."""
        self.close()
        self._connection = self._setup_connection()

    @backoff.on_exception(
        wait_gen=backoff.fibo,
        exception=(LDAPSocketSendError,),
        max_tries=2,
        logger=logger,
        on_backoff=lambda details: cast(
            "LDAPConnector", details["args"][0]
        ).reconnect(),
    )
    def _fetch(self, limit: int, **filters: str | None) -> list[dict[str, Any]]:
        """Fetch all items that match the given filters.

        Args:
            limit: How many items to return
            filters: LDAP compatible filters, will be joined in AND-condition

        Returns:
            List of raw ldap items
        """
        search_filter = "".join(
            f"({key}={value})" for key, value in filters.items() if value
        )
        response = self._connection.extend.standard.paged_search(
            search_base=self._search_base,
            search_filter=f"(&{search_filter})",
            attributes=tuple(sorted(LDAPPerson.model_fields)),
            generator=False,
            size_limit=limit,
        )
        return [
            attributes for item in response if (attributes := item.get("attributes"))
        ]

    def get_persons_or_functional_accounts(
        self,
        *,
        displayName: str = "*",  # noqa: N803
        limit: int = 10,
        **filters: str | None,
    ) -> list[AnyLDAPActor]:
        """Get LDAP persons or functional accounts that match provided filters.

        Args:
            displayName: Display name of the items to find
            limit: How many items to return
            **filters: Additional filters

        Returns:
            List of LDAP persons and functional accounts
        """
        raw_items = self._fetch(
            limit=limit,
            objectCategory="Person",
            displayName=displayName,
            **filters,
        )
        return [LDAPActorTypeAdapter.validate_python(item) for item in raw_items]

    def get_functional_accounts(
        self,
        *,
        mail: str = "*",
        objectGUID: str = "*",  # noqa: N803
        sAMAccountName: str = "*",  # noqa: N803
        limit: int = 10,
        **filters: str | None,
    ) -> list[LDAPFunctionalAccount]:
        """Get LDAP functional accounts that match provided filters.

        Some projects/resources declare functional mailboxes as their contact.

        Args:
            mail: Email address of the functional account
            objectGUID: Internal LDAP identifier
            sAMAccountName: Account name
            limit: How many items to return
            **filters: Additional filters

        Returns:
            List of LDAP functional accounts
        """
        raw_items = self._fetch(
            limit=limit,
            mail=mail,
            objectCategory="Person",
            objectGUID=objectGUID,
            OU="Funktion",
            sAMAccountName=sAMAccountName,
            **filters,
        )
        return [LDAPFunctionalAccount.model_validate(item) for item in raw_items]

    def get_persons(  # noqa: PLR0913
        self,
        *,
        employeeID: str = "*",  # noqa: N803
        given_name: str = "*",
        mail: str = "*",
        objectGUID: str = "*",  # noqa: N803
        sAMAccountName: str = "*",  # noqa: N803
        surname: str = "*",
        limit: int = 10,
        **filters: str | None,
    ) -> list[LDAPPerson]:
        """Get LDAP persons that match the provided filters.

        An LDAP person's objectGUIDs is stable across name changes, whereas name based
        person identifiers of the schema SurnameF are not stable.

        Only consider LDAP entries of objectClass 'user', ObjectCategory 'Person'.
        Additional required attributes are: sAMAccountName, employeeID.

        Args:
            employeeID: Employee identifier
            given_name: Given name of a person, defaults to non-null
            mail: Email address, defaults to non-null
            objectGUID: Internal LDAP identifier
            sAMAccountName: Account name
            surname: Surname of a person, defaults to non-null
            limit: How many items to return
            **filters: Additional filters

        Returns:
            List of LDAP persons
        """
        raw_items = self._fetch(
            limit=limit,
            objectClass="user",
            objectCategory="Person",
            employeeID=employeeID,
            givenName=given_name,
            mail=mail,
            objectGUID=objectGUID,
            sAMAccountName=sAMAccountName,
            sn=surname,
            **filters,
        )
        return [LDAPPerson.model_validate(item) for item in raw_items]

    def get_functional_account(
        self,
        *,
        mail: str = "*",
        objectGUID: str = "*",  # noqa: N803
        sAMAccountName: str = "*",  # noqa: N803
        **filters: str | None,
    ) -> LDAPFunctionalAccount:
        """Get a single LDAP functional account for the given filters.

        Args:
            mail: Email address of the functional account
            objectGUID: Internal LDAP identifier
            sAMAccountName: Account name
            **filters: Filters for LDAP search

        Raises:
            MExError: If number of LDAP entries that match the filters is not 1

        Returns:
            Single LDAP functional account matching the filters
        """
        functional_accounts = self.get_functional_accounts(
            mail=mail,
            objectGUID=objectGUID,
            sAMAccountName=sAMAccountName,
            limit=2,
            **filters,
        )
        if not functional_accounts:
            msg = (
                "Cannot find AD functional account for filters "
                f"'objectGUID: {objectGUID}, {filters}'"
            )
            raise EmptySearchResultError(msg)
        if len(functional_accounts) > 1:
            msg = (
                "Found multiple AD functional accounts for filters "
                f"'objectGUID: {objectGUID}, {filters}'"
            )
            raise FoundMoreThanOneError(msg)
        return functional_accounts[0]

    def get_person(  # noqa: PLR0913
        self,
        *,
        employeeID: str = "*",  # noqa: N803
        given_name: str = "*",
        mail: str = "*",
        objectGUID: str = "*",  # noqa: N803
        sAMAccountName: str = "*",  # noqa: N803
        surname: str = "*",
        **filters: str | None,
    ) -> LDAPPerson:
        """Get a single LDAP person for the given filters.

        Args:
            employeeID: Employee ID, must be present
            given_name: Given name of a person, defaults to non-null
            mail: Email address, defaults to non-null
            objectGUID: Internal LDAP identifier
            sAMAccountName: str = "*",  # noqa: N803
            surname: Surname of a person, defaults to non-null
            **filters: Filters for LDAP search

        Raises:
            MExError: If number of LDAP entries that match the filters is not 1

        Returns:
            Single LDAP person matching the filters
        """
        persons = self.get_persons(
            employeeID=employeeID,
            given_name=given_name,
            mail=mail,
            objectGUID=objectGUID,
            sAMAccountName=sAMAccountName,
            surname=surname,
            limit=2,
            **filters,
        )
        if not persons:
            msg = (
                f"Cannot find AD person for filters 'objectGUID: {objectGUID}, "
                f"employeeID: {employeeID}, {filters}'"
            )
            raise EmptySearchResultError(msg)
        if len(persons) > 1:
            msg = (
                f"Found multiple AD persons for filters 'objectGUID: {objectGUID}, "
                f"employeeID: {employeeID}, {filters}'"
            )
            raise FoundMoreThanOneError(msg)
        return persons[0]
