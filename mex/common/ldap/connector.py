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
from mex.common.ldap.models import LDAPActor, LDAPPerson, LDAPUnit
from mex.common.settings import BaseSettings

_LDAPActorT = TypeVar("_LDAPActorT", bound=LDAPActor)


class LDAPConnector(BaseConnector):
    """Connector class to handle credentials and querying of LDAP."""

    def __init__(self) -> None:
        """Create a new LDAP connection."""
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
        self._connection = connection.__enter__()
        self._search_base = settings.ldap_search_base
        if not self._is_service_available():
            msg = f"LDAP service not available at url: {host}:{port}"
            raise MExError(msg)

    def _is_service_available(self) -> bool:
        try:
            return self._connection.server.check_availability() is True
        except LDAPExceptionError:
            return False

    def close(self) -> None:
        """Close the connector's underlying LDAP connection."""
        self._connection.__exit__(None, None, None)

    def _fetch(
        self,
        model_cls: type[_LDAPActorT],
        limit: int = 10,
        **filters: str,
    ) -> list[_LDAPActorT]:
        """Fetch all items that match the given filters and parse to given model.

        Args:
            model_cls: Pydantic model class
            limit: How many items to return
            **filters: LDAP compatible filters, will be joined in AND-condition

        Returns:
            List of instances of `model_cls`
        """
        search_filter = "".join(f"({key}={value})" for key, value in filters.items())
        response = self._connection.extend.standard.paged_search(
            search_base=self._search_base,
            search_filter=f"(&{search_filter})",
            attributes=model_cls.get_ldap_fields(),
            generator=False,
            size_limit=limit,
        )
        return [
            model_cls.model_validate(attributes)
            for item in response
            if (attributes := item.get("attributes"))
        ]

    def get_functional_accounts(
        self,
        mail: str = "*",
        sAMAccountName: str = "*",  # noqa: N803
        limit: int = 10,
        **filters: str,
    ) -> list[LDAPActor]:
        """Get LDAP functional accounts that match provided filters.

        Some projects/resources declare functional mailboxes as their contact.

        Args:
            mail: Email address of the functional account
            sAMAccountName: Account name
            limit: How many items to return
            **filters: Additional filters

        Returns:
            List of LDAP functional accounts
        """
        return self._fetch(
            LDAPUnit,
            objectCategory="Person",
            OU="Funktion",
            sAMAccountName=sAMAccountName,
            mail=mail,
            limit=limit,
            **filters,
        )

    def get_persons(
        self,
        surname: str = "*",
        given_name: str = "*",
        mail: str = "*",
        limit: int = 10,
        **filters: str,
    ) -> list[LDAPPerson]:
        """Get LDAP persons that match the provided filters.

        An LDAP person's objectGUIDs is stable across name changes, whereas name based
        person identifiers of the schema SurnameF are not stable.

        Only consider LDAP entries of objectClass 'user', ObjectCategory 'Person'.
        Additional required attributes are: sAMAccountName, employeeId.

        Args:
            given_name: Given name of a person, defaults to non-null
            surname: Surname of a person, defaults to non-null
            mail: Email address, defaults to non-null
            limit: How many items to return
            **filters: Additional filters

        Returns:
            List of LDAP persons
        """
        return self._fetch(
            LDAPPerson,
            objectClass="user",
            objectCategory="Person",
            sAMAccountName="*",
            employeeId="*",
            mail=mail,
            sn=surname,
            givenName=given_name,
            limit=limit,
            **filters,
        )

    def get_functional_account(
        self,
        objectGUID: str = "*",  # noqa: N803
        **filters: str,
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
        functional_accounts = self.get_functional_accounts(
            objectGUID=objectGUID,
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

    def get_person(
        self,
        objectGUID: str = "*",  # noqa: N803
        employeeID: str = "*",  # noqa: N803
        **filters: str,
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
        persons = self.get_persons(
            objectGUID=objectGUID,
            employeeID=employeeID,
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
