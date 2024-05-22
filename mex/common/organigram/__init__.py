"""Helper extractor to extract organigram data.

Common use cases:
- extract organizational units of your organization (e.g. president, departments, units)

Configuration
-------------

The extractor reads data from a json file, whose path is set with the settings parameter
`organigram_path` (see `mex.common.settings` for further info).

Extracting data
---------------

The module `organigram.extract` contains functions for data extraction.

Transforming data
-----------------

The module `organigram.transform` contains functions for data transformation.

Use the `stableTargetId` attribute of the transformed objects to set attributes
requiring an `MergedOrganizationalUnitIdentifier`.

Convenience Functions
---------------------

The module `organigram.extract` holds convenience functions, e.g. for building a mapping
from email addresses or synonyms to `ExtractedOrganizationalUnit`.

JSON file format
----------------

See example file in `assets/raw-data/organigram/organizational_units.json`.
For mandatory / optional attributes, see model in `mex/common/organigram/models.py`.
"""
