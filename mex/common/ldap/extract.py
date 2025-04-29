from collections import defaultdict
from collections.abc import Iterable

from mex.common.identity import get_provider
from mex.common.ldap.connector import LDAPConnector
from mex.common.ldap.models import LDAPPerson, LDAPPersonWithQuery
from mex.common.models import ExtractedPrimarySource
from mex.common.types import MergedPersonIdentifier


def _get_merged_ids_by_attribute(
    attribute: str,
    persons: Iterable[LDAPPerson],
    primary_source: ExtractedPrimarySource,
) -> dict[str, list[MergedPersonIdentifier]]:
    """Return mapping from dynamic Person attribute to corresponding merged person ids.

    MergedPersonIdentifiers are looked up in the identity provider and will be omitted
    for any person that has not yet been assigned an `Identity` there.

    Args:
        attribute: The key to use for the resulting mapping
        persons: Iterable of LDAP persons
        primary_source: Primary source for LDAP

    Returns:
        Mapping from a stringified `LDAPPerson[attribute]` to corresponding
        MergedPersonIdentifiers
    """
    if attribute not in LDAPPerson.model_fields:
        msg = f"Not a valid LDAPPerson field: {attribute}"
        raise RuntimeError(msg)
    merged_ids_by_attribute = defaultdict(list)
    provider = get_provider()
    for person in persons:
        if identities := provider.fetch(
            had_primary_source=primary_source.stableTargetId,
            identifier_in_primary_source=str(person.objectGUID),
        ):
            attribute_values = getattr(person, attribute)
            merged_id = MergedPersonIdentifier(identities[0].stableTargetId)
            if isinstance(attribute_values, Iterable) and not isinstance(
                attribute_values, str
            ):
                for value in attribute_values:
                    merged_ids_by_attribute[str(value)].append(merged_id)
            else:
                merged_ids_by_attribute[str(attribute_values)].append(merged_id)
    return merged_ids_by_attribute


def get_merged_ids_by_employee_ids(
    persons: Iterable[LDAPPerson], primary_source: ExtractedPrimarySource
) -> dict[str, list[MergedPersonIdentifier]]:
    """Return a mapping from a person's employeeID to their merged person ids.

    MergedPersonIdentifiers are looked up in the identity provider and will be omitted
    for any person that has not yet been assigned an `Identity` there.

    Args:
        persons: Iterable of LDAP persons
        primary_source: Primary source for LDAP

    Returns:
        Mapping from `LDAPPerson.employeeID` to corresponding MergedPersonIdentifiers
    """
    return _get_merged_ids_by_attribute("employeeID", persons, primary_source)


def get_merged_ids_by_email(
    persons: Iterable[LDAPPerson], primary_source: ExtractedPrimarySource
) -> dict[str, list[MergedPersonIdentifier]]:
    """Return a mapping from a person's e-mail to their merged person ids.

    MergedPersonIdentifiers are looked up in the identity provider and will be omitted
    for any person that has not yet been assigned an `Identity` there.

    Args:
        persons: Iterable of LDP persons
        primary_source: Primary source for LDAP

    Returns:
        Mapping from `LDAPPerson.mail` to corresponding MergedPersonIdentifiers
    """
    return _get_merged_ids_by_attribute("mail", persons, primary_source)


def get_merged_ids_by_query_string(
    persons_with_query: Iterable[LDAPPersonWithQuery],
    primary_source: ExtractedPrimarySource,
) -> dict[str, list[MergedPersonIdentifier]]:
    """Return a mapping from a person query string to their merged person ids.

    MergedPersonIdentifiers are looked up in the identity provider and will be omitted
    for any person that has not yet been assigned an `Identity` there.

    Args:
        persons_with_query: Iterable of LDP persons with query
        primary_source: Primary source for LDAP

    Returns:
        Mapping from `LDAPPersonWithQuery.query` to corresponding
        MergedPersonIdentifiers
    """
    merged_ids_by_attribute = defaultdict(list)
    provider = get_provider()
    for person_with_query in persons_with_query:
        if identities := provider.fetch(
            had_primary_source=primary_source.stableTargetId,
            identifier_in_primary_source=str(person_with_query.person.objectGUID),
        ):
            merged_ids_by_attribute[str(person_with_query.query)].append(
                MergedPersonIdentifier(identities[0].stableTargetId)
            )
    return merged_ids_by_attribute


def get_ldap_persons(
    displayName: str | None,  # noqa: N803
    limit: int = 10,
) -> list[LDAPPerson]:
    """Get all ldap persons matching the filters.

    Args:
        displayName: Display name of a person
        limit: How many items to return

    Returns:
        List of LDAP persons
    """
    connector = LDAPConnector.get()
    return connector.get_persons(
        displayName=displayName,
        limit=limit,
    )
