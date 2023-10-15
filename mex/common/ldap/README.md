Helper extractor to extract data from ldap. 

Common use cases are e.g. extracting employee accounts or functional accounts of your
organization.

Possible queries are for example the account name, surname, given name, or email. 

For configuring the ldap connection, set the settings parameter `ldap_url` (see settings 
docs (TODO: link to settings docs) for how to do this) to an url in the format 
`ldap://user:pw@ldap:636`, where

- `user` is the username and
- `pw` is the password for authenticating against ldap
- `ldap` is the url of the ldap server
- `636` is the port of the ldap server

A working minimal example:

```python
from itertools import tee
from mex.common.ldap.connector import LDAPConnector
from mex.common.ldap.transform import transform_ldap_person_to_mex_person
from mex.common.sinks.load import load
from mex.common.primary_source.extract import extract_seed_primary_sources
from mex.common.primary_source.transform import (
    get_primary_sources_by_name,
    transform_seed_primary_sources_to_extracted_primary_sources,
)
from mex.common.organigram.extract import extract_organigram_units
from mex.common.organigram.transform import (
    transform_organigram_units_to_organizational_units,
)
# we need the ldap primary source for setting the primary source of each extracted 
# ldap-person (where we extracted the data from) and the organigram to link persons to 
# their organizational unit.

seed_primary_sources = extract_seed_primary_sources()
extracted_primary_sources = (
    transform_seed_primary_sources_to_extracted_primary_sources(
        seed_primary_sources
    )
)
(
    extracted_primary_source_mex,  # the base primary source, all extracted primary sources have this as their primarySource
    extracted_primary_source_ldap,
    extracted_primary_source_organigram,
) = get_primary_sources_by_name(
    extracted_primary_sources, "mex", "ldap", "organigram"
)
load(
    [
        extracted_primary_source_mex,
        extracted_primary_source_ldap,
        extracted_primary_source_organigram,
    ]
)

# extracting the organigram

organigram_units = extract_organigram_units()
mex_organizational_units = transform_organigram_units_to_organizational_units(
    organigram_units, extracted_primary_source_organigram
)
mex_organizational_unit_gens = tee(mex_organizational_units, 2)
load(mex_organizational_unit_gens[0])

units_by_identifier_in_primary_source = {
    unit.identifierInPrimarySource: unit
    for unit in mex_organizational_unit_gens[1]
}

# extracting a person from ldap

ldap = LDAPConnector.get()
ldap_persons = list(ldap.get_persons(surname="Mustermann", given_name="Max"))
if len(ldap_persons) == 1 and ldap_persons[0].objectGUID:
    ldap_person = ldap_persons[0]
else:
    raise KeyError("No ldap person found with name 'Max Mustermann'")

# Before loading this person into mex via `mex.common.sinks.load`, we need to transform it into a MEx Person:

mex_person = transform_ldap_person_to_mex_person(
    ldap_person, 
    extracted_primary_source_ldap,
    units_by_identifier_in_primary_source,
)

# and finally load it into mex

load(mex_person)
```

The `mex_person.stableTargetId` attribute can be used in any entity that requires a 
`PersonID`.
