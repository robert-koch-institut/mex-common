import re
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
    LDAP_MODEL_CLASSES,
    AnyLDAPActor,
    AnyLDAPActorsTypeAdapter,
    LDAPFunctionalAccount,
    LDAPFunctionalAccountsTypeAdapter,
    LDAPPerson,
    LDAPPersonsTypeAdapter,
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
    def _fetch(self, search_filter: str, limit: int) -> list[dict[str, Any]]:
        """Fetch all items that match the given filters.

        Args:
            search_filter: LDAP search query
            limit: How many items to return

        Returns:
            List of raw ldap items
        """
        response = self._connection.extend.standard.paged_search(
            search_base=self._search_base,
            search_filter=search_filter.strip(),
            attributes=tuple(
                sorted({f for m in LDAP_MODEL_CLASSES for f in m.model_fields})
            ),
            size_limit=limit,
        )
        return [
            attributes for item in response if (attributes := item.get("attributes"))
        ]

    @staticmethod
    def _sanitize(value: str) -> str:
        """Sanitize a query value by removing invalid chars."""
        return re.sub(r"[^a-zA-ZÀ-ÿ0-9\*\.\-_@ ]+", "*", value)

    def get_persons_or_functional_accounts(
        self,
        *,
        query: str = "*",
        limit: int = 10,
    ) -> list[AnyLDAPActor]:
        """Get LDAP persons or functional accounts.

        Args:
            query: Display name of person or email of functional account
            limit: How many items to return

        Returns:
            List of LDAP persons and/or functional accounts
        """
        search_filter = f"""
        (|
            (&
                (objectCategory=Person)
                (sAMAccountName=*)
                (employeeID=*)
                (displayName={self._sanitize(query)})
            )
            (&
                (objectCategory=Person)
                (OU=Funktion)
                (mail={self._sanitize(query)})
            )
        )
        """
        raw_items = self._fetch(search_filter, limit)
        return AnyLDAPActorsTypeAdapter.validate_python(raw_items)

    def get_functional_accounts(
        self,
        *,
        mail: str = "*",
        limit: int = 10,
    ) -> list[LDAPFunctionalAccount]:
        """Get LDAP functional accounts that match provided filters.

        Some projects/resources declare functional mailboxes as their contact.

        Args:
            mail: Email address of the functional account
            limit: How many items to return

        Returns:
            List of LDAP functional accounts
        """
        search_filter = f"""
        (&
            (objectCategory=Person)
            (OU=Funktion)
            (mail={self._sanitize(mail)})
        )
        """
        raw_items = self._fetch(search_filter, limit)
        return LDAPFunctionalAccountsTypeAdapter.validate_python(raw_items)

    def get_persons(  # noqa: PLR0913
        self,
        *,
        display_name: str = "*",
        employee_id: str = "*",
        given_name: str = "*",
        mail: str = "*",
        object_guid: str = "*",
        sam_account_name: str = "*",
        surname: str = "*",
        limit: int = 10,
    ) -> list[LDAPPerson]:
        """Get LDAP persons that match the provided filters.

        An LDAP person's objectGUIDs is stable across name changes, whereas name based
        person identifiers of the schema SurnameF are not stable.

        Args:
            display_name: Display name of the person
            employee_id: Employee identifier
            given_name: Given name of a person, defaults to non-null
            mail: Email address, defaults to non-null
            object_guid: Internal LDAP identifier
            sam_account_name: Account name
            surname: Surname of a person, defaults to non-null
            limit: How many items to return

        Returns:
            List of LDAP persons
        """
        search_filter = f"""
        (&
            (objectCategory=Person)
            (displayName={self._sanitize(display_name)})
            (employeeID={self._sanitize(employee_id)})
            (givenName={self._sanitize(given_name)})
            (mail={self._sanitize(mail)})
            (objectGUID={self._sanitize(object_guid)})
            (sAMAccountName={self._sanitize(sam_account_name)})
            (sn={self._sanitize(surname)})
        )
        """
        raw_items = self._fetch(search_filter, limit)
        return LDAPPersonsTypeAdapter.validate_python(raw_items)

    def get_functional_account(
        self,
        *,
        mail: str = "*",
    ) -> LDAPFunctionalAccount:
        """Get a single LDAP functional account for the given mail address.

        Args:
            mail: Email address of the functional account

        Raises:
            EmptySearchResultError: If no LDAP entry matching filters was found
            FoundMoreThanOneError: If more than one LDAP entry was found

        Returns:
            Single LDAP functional account
        """
        functional_accounts = self.get_functional_accounts(mail=mail, limit=2)
        if not functional_accounts:
            msg = f"Cannot find AD functional account for filters mail: {mail}"
            raise EmptySearchResultError(msg)
        if len(functional_accounts) > 1:
            msg = f"Found multiple AD functional accounts for mail: {mail}"
            raise FoundMoreThanOneError(msg)
        return functional_accounts[0]

    def get_person(  # noqa: PLR0913
        self,
        *,
        display_name: str = "*",
        employee_id: str = "*",
        given_name: str = "*",
        mail: str = "*",
        object_guid: str = "*",
        sam_account_name: str = "*",
        surname: str = "*",
    ) -> LDAPPerson:
        """Get a single LDAP person for the given filters.

        Args:
            display_name: Display name of the person
            employee_id: Employee identifier
            given_name: Given name of a person, defaults to non-null
            mail: Email address, defaults to non-null
            object_guid: Internal LDAP identifier
            sam_account_name: Account name
            surname: Surname of a person, defaults to non-null

        Raises:
            EmptySearchResultError: If no LDAP entry matching filters was found
            FoundMoreThanOneError: If more than one LDAP entry was found

        Returns:
            Single LDAP person matching the filters
        """
        persons = self.get_persons(
            employee_id=employee_id,
            given_name=given_name,
            mail=mail,
            object_guid=object_guid,
            sam_account_name=sam_account_name,
            surname=surname,
            display_name=display_name,
            limit=2,
        )
        if not persons:
            msg = "Cannot find AD person for filters"
            raise EmptySearchResultError(msg)
        if len(persons) > 1:
            msg = "Found multiple AD persons for filters"
            raise FoundMoreThanOneError(msg)
        return persons[0]
