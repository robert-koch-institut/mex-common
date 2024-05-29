"""Helper extractor to get metadata primary sources.

It represents the original source of metadata that all the data in MEx will attach to.
For example `confluence-vvt` primary source means: data extracted from `confluence-vvt`
x-system will be attached to this primary source.

Common use cases
----------------

- extract info of a particular primary source to attach extracted metadata to

Configuration
-------------

To configure primary_source extractor, set `primary_sources_path` in settings to point
to `primary-sources.json` in `mex-assets` repository. A sample primary sources file is
also included in `mex-extractors` at
`assets/raw-data/primary-sources/primary-sources.json` for testing purposes.

Extracting primary sources
--------------------------

Use `extract_seed_primary_sources` in `primary_source.extract` function to extract all
primary sources. This function will yield all the primary sources available in
`primary_sources.json` source file.

Transforming primary sources
----------------------------

Use `transform_seed_primary_sources_to_extracted_primary_sources` in
`primary_sources.transform` to get `ExtractedPrimarySource`. This function will yield
all the primary sources, which is often not required.

So to filter out only the required x-system primary sources use
`get_primary_sources_by_name` in `primary_sources.transform`. This function needs
Iterable from step-1 and names of the required x-systems. For example by passing names
as `mex`, `ldap`, `confluence-vvt` will return `ExtractedPrimarySource` of these
x-systems.
"""
