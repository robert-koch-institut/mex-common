"""Helper extractor to extract data from Lightweight Directory Access Protocol (LDAP).

Common use cases:
- extract employee accounts of your organization
- extract functional accounts of your organization

Possible queries are for example the account name, surname, given name, or email.

Configuration
-------------

For configuring the ldap connection, set the settings parameter `ldap_url`
(see `mex.common.settings` for further info) to an LDAP url (see
 https://datatracker.ietf.org/doc/html/rfc2255#section-3 for further information).

Extracting data
---------------

Use the `LDAPConnector` from the `ldap.connector` module to extract data.

Transforming data
-----------------

The module `ldap.transform` contains functions for transforming LDAP data into MEx
models.

The `mex_person.stableTargetId` attribute can be used in any entity that requires a
`MergedPersonIdentifier`.

Convenience Functions
---------------------

The module `ldap.extract` holds convenience functions, e.g. for build a mapping from
query strings to `stableTargetId`s.

"""
