# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changes

### Deprecated

### Removed

### Fixed

### Security

## [1.0.0] - 2025-08-21

### Added

- add `Validation` enum to `mex.common.types`
- add `ensure_list` utility function

### Changes

- BREAKING: change validation argument of `create_merged_item` helper
- BREAKING: change the behavior of merge previews to include blocked values
- BREAKING: change model hash and string computation to faster black2/pickle

### Removed

- BREAKING: remove unused `BaseModel.checksum` method

## [0.65.0] - 2025-07-25

### Added

- add identifier filter to merged and preview fetch endpoints in BackendApiConnector
- add `fetch_all_merged_items` and `get_extracted_item` methods to BackendApiConnector

### Changes

- BREAKING: replace hadPrimarySource with reference field filter in BackendApiConnector
- BREAKING: BackendApiConnector fetch endpoint methods now expect keyword arguments
- bump cookiecutter template to e886ec

## [0.64.0] - 2025-07-24

### Changes

- use default wiki label should there be neither a german nor english label

## [0.63.0] - 2025-07-10

### Added

- BREAKING: add RKI organization as unitOf to organigram units

## [0.62.2] - 2025-07-08

### Fixed

- fix ldap connection resetting

## [0.62.1] - 2025-07-07

### Added

- moved `contains_any_types` over from mex-backend

### Changes

- ensure extracted items are merged in predictable way
- improve a batch of doc-strings with args, raises and return sections

### Fixed

- fix ldap error if ldap connector is >1h old

## [0.62.0] - 2025-06-17

### Added

- running github release action publishes to pypi

### Changes

- use mex-model from pypi instead of github

## [0.61.2] - 2025-06-13

### Changes

- bump mex-model dependency
- get vocabulary model examples dynamically from models

## [0.61.1] - 2025-05-19

### Changes

- improve logging for backend API sink connector

### Fixed

- fix response type of `BackendApiConnector.preview_merged_item` to be `PreviewModel`

## [0.61.0] - 2025-05-16

### Added

- add proportional backoff to too_many_requests responses and configure minimum time

### Changes

- move hash function from ExtractedData to BaseModel
- added fullname attribute to transforming orcid person to mex person

### Removed

- removed `BaseEntity` class to reduce inheritance hierarchy
- remove http retry on forbidden responses

## [0.60.0] - 2025-05-13

### Added

- added MEX_BACKEND_API_PARALLELIZATION and MEX_BACKEND_API_CHUNK_SIZE settings
- added support for sending batches of data to the backend in parallel

### Changes

- bump cookiecutter template to ed5deb

## [0.59.2] - 2025-05-12

### Changes

- update pyarrow and click dependencies
- update mex-model to 3.6.1

## [0.59.1] - 2025-04-29

### Changes

- update mex-model to 3.5.7

### Fixed

- fix ldap connector method signatures

## [0.59.0] - 2025-04-29

### Added

- added `BackendApiConnector` methods to create and update rule-sets
- added `BackendApiConnector` methods to search in wiki, ldap and orcid
- added `BackendApiConnector` methods to fetch and assign identities
- added `limit` parameter to ldap connector and helper functions
- added pre-configured type adapters to all models with an `entityType`
- added `MEX_LDAP_SEARCH_BASE` setting to configure the search domain
- added `metrics` method to connectors to collect cache hits and misses
- added `get_extracted_organizational_unit_with_parents` organigram helper
- added `transform_organigram_unit_to_extracted_organizational_unit` transformer

### Changes

- BREAKING: move MergedModel and RuleSetResponse type adapters to models module
- de-coupled BackendApiIdentityProvider from BackendApiConnector
- moved memory and backend identity provider registration to package init file
- BREAKING: convert ldap connector and related functions from generator to list returns
- reconfigure all cached functions to have a `maxsize` setting
- moved `get_alias_lookup`, `get_list_field_names` and `get_field_names_allowing_none`
  from `BaseModel` class to utils module
- BREAKING: convert organigram functions from generator to list returns
- BREAKING: convert primary-source functions from generator to list return
- BREAKING: moved `split_to_caps` from types to transform module
- BREAKING: moved `normalize` from utils to transform module
- BREAKING: renamed `get_persons_by_name` to `get_ldap_persons`

### Removed

- BREAKING: remove return value from `BackendApiConnector.ingest`
- BREAKING: remove unused `LDAPConnector.get_unit` and `get_units` methods
- BREAKING: remove `get_count_of_found_persons_by_name` to avoid duplicate queries
- BREAKING: removed `member_of` validation for ldap persons
- BREAKING: removed `get_all_extracted_primary_sources` helper

## [0.58.3] - 2025-04-24

### Added

- Also allow raw request of HTTPConnector

## [0.58.2] - 2025-04-22

### Changes

- increase read timeout limit for BackendApiSink

## [0.58.1] - 2025-04-17

### Changes

- log model info on sink errors

## [0.58.0] - 2025-04-11

### Changes

- move ingest timeout configuration from BackendAPIConnector to BackendApiSink
- wrap read time out errors of http connector in a custom timed error
- add proportional backoff to http connector: the longer it took, the longer we chill
- use watch decorator on sinks to only log once every 1000 write ops

## [0.57.0] - 2025-04-09

### Added

- add pagination to orcid connector search method
- add caching to orcid single item lookup
- add support for multiple emails to orcid transform

### Changes

- BREAKING: dissolve aux-extractor model folders into single files
- BREAKING: clean-up orcid connector method and extract function names
- BREAKING: require orcid primary source as parameter to transform function
- make orcid family and given names optional to validate all data
- rename private _get_organization_details to public get_wikidata_organization

### Removed

- drop stale DataType type
- remove unused LDAPConnector.PAGE_SIZE
- BREAKING: removed unused MEX_WIKI_QUERY_SERVICE_URL setting
- BREAKING: removed unused WikidataQueryServiceConnector class
- BREAKING: removed unused search_organization_by_label extract function
- BREAKING: removed unused get_count_of_found_organizations_by_label extract function
- BREAKING: removed unused search_organizations_by_label extract function
- BREAKING: removed unused get_extracted_organization_from_wikidata helper function

## [0.56.1] - 2025-03-31

### Added

- ALL_TYPES_BY_FIELDS_BY_CLASS_NAMES and VOCABULARIES_BY_FIELDS_BY_CLASS_NAMES lookups

### Changes

- update ruff and apply TC006 fixes

## [0.56.0] - 2025-03-27

### Added

- extract method for orcid can now obtain multiple results (orcid records)

## [0.55.0] - 2025-03-21

### Changes

- BREAKING: wrap function around watch decorator accepting log_interval parameter
- increase parse_csv default chunksize to 10000 and log chunks instead of rows

## [0.54.4] - 2025-03-20

### Changes

- reduce chunk size for backend api sink to avoid timeouts

## [0.54.3] - 2025-03-18

### Fixed

- stop stringifying backend identity provider url parameters

## [0.54.2] - 2025-03-05

### Fixed

- remove unsafe pytest import from testing plugin

## [0.54.1] - 2025-02-28

### Changes

- BREAKING: mex-model to 3.5.6: make doi pattern more lenient

## [0.54.0] - 2025-02-27

### Changes

- BREAKING: mex-model to 3.5.5: update patterns and examples for URL fields

## [0.53.0] - 2025-02-26

### Added

- BREAKING: filter for had_primary_source to backend api connector

## [0.52.2] - 2025-02-24

### Fixed

- temporarily pin pydantic settings version to bypass error in settings update.

## [0.52.1] - 2025-02-24

## [0.52.0] - 2025-02-19

### Added

- Connector class for retrieving ORCID data by ID or name
- methods for extracting data from orcid
- methods to transform from OrcidPerson to mex person
- model class for orcid data
- unit tests for orcid connector

## [0.51.1] - 2025-02-13

### Fixed

- expand the pattern for DOI Urls as these can also contain lowercase letters

## [0.51.0] - 2025-02-11

### Added

- add entry for `s3` to sink settings enum

### Changes

- add `AnyMergedModel` to the allowed types for `Sink.load` methods
- but let BackendApiSink throw an error, when merged items are loaded
- make local typevars private and give them speaking names

## [0.50.0] - 2025-02-06

### Changes

- BREAKING: move ItemsContainer and PaginatedItemsContainer to mex.common.models
- BREAKING: replace post_extracted_items with ingest and allow AnyRuleSetResponses
- allow AnyRuleSetResponses as arguments to sinks
- BREAKING: sinks now yield the models they loaded, instead of just their identifiers

## [0.49.3] - 2025-01-29

### Changes

- update mex-model to 3.5.1

### Fixed

- fix regex pattern for GndIdStr in organization models

## [0.49.2] - 2025-01-29

### Fixed

- do not wrap field types in `setValues` in mapping rules in another list

## [0.49.1] - 2025-01-29

### Fixed

- reduce Filter classes to a single list field of `FilterField` items

## [0.49.0] - 2025-01-29

### Added

- new (partially generic) classes for defining Mapping and Filter fields and rules

### Changes

- BREAKING: replaced dynamic Mapping and Filter classes with static ones

### Deprecated

- use FILTER_MODEL_CLASSES_BY_NAME instead of FILTER_MODEL_BY_EXTRACTED_CLASS_NAME
- use MAPPING_MODEL_CLASSES_BY_NAME instead of MAPPING_MODEL_BY_EXTRACTED_CLASS_NAME

## [0.48.0] - 2025-01-28

### Added

- add a sink registry with `register_sink` and `get_sink` functions
- add a multi-sink implementation, akin to `mex.extractors.load`

### Changes

- BREAKING: convert post_to_backend_api to BackendApiSink
- BREAKING: convert write_ndjson to NdjsonSink
- backend and ndjson sinks log progress only in batches
- increase timeout and decrease chunk size for backend API sink
- port backend identity provider implementation from editor/extractors to common
- allow backend and graph as identity provider setting to simplify setting subclasses,
  even though graph is not implemented in mex-common
- BREAKING: make backend api connector response models generic, to keep DRY

## [0.47.1] - 2025-01-24

### Fixed

- skip None values when merging extracted and rule items

## [0.47.0] - 2025-01-23

### Added

- merging logic to mex-common

## [0.46.0] - 2025-01-09

### Added

- BREAKING: add nested models (Text, Link) to *all* lookups in `mex.common.fields`

### Changes

- BREAKING: move `GenericFieldInfo` from `models.base.field_info` to `utils`
- BREAKING: move `get_all_fields` from `BaseModel` to `utils` to support all base models

## [0.45.0] - 2024-12-18

### Changes

- BREAKING: change type of distribution.title to an array of texts

## [0.44.0] - 2024-12-12

### Changes

- updated ldap search from name and familyname to one single attribute "displayname"

## [0.43.0] - 2024-12-10

### Added

- add preview models for merged items without cardinality validation
- BREAKING: preview models are now part of all `mex.common.fields` lookups
- add `BackendApiConnector.fetch_preview_items` for fetching previews

### Deprecated

- stop using `ExtractedData`, use `AnyExtractedModel` instead
- stop using `MergedItem`, use `AnyMergedModel` instead
- stop using `AdditiveRule`, use `AnyAdditiveRule` instead
- stop using `SubtractiveRule`, use `AnySubtractiveRule` instead
- stop using `PreventiveRule`, use `AnyPreventiveRule` instead
- stop using `BaseEntity`, use a concrete union instead

### Removed

- removed deprecated `BulkInsertResponse` as alias for `IdentifiersResponse`
- removed unused module export of `mex.common.models.generate_entity_filter_schema`
- removed unused module export of `mex.common.models.generate_mapping_schema`
- drop export `models.ExtractedPrimarySourceIdentifier`, import from `types` instead
- drop export `models.MergedPrimarySourceIdentifier`, import from `types` instead

## [0.42.0] - 2024-12-02

### Added

- add vocabulary and temporal unions and lookups to `mex.common.types`
- add `mex.common.fields` with field type by class name lookups

### Changes

- wikidata helper now optionally accepts wikidata primary source
- set default empty rules to all of the rule-set models
- pin pydantic to sub 2.10 (for now) because of breaking changes

### Fixed

- switch HTTP method for preview endpoint to `POST`
- add optional values to variadic values for distribution models
- make `endpointDescription` optional for variadic access platform models

## [0.41.0] - 2024-11-18

### Added

- organigram extraction checks for duplicate emails/labels in different organigram units

### Changes

- upgrade mex-model dependency to version 3.2

## [0.40.0] - 2024-10-28

### Changes

- upgrade mex-model dependency to version 3.1

### Fixed

- fix typo in `repositoryURL` of bibliographic resources
- make identifier and stableTargetId of ExtractedBibliographicResource computed fields

## [0.39.0] - 2024-10-28

### Added

- added new consent and bibliography reference models and vocabs
- added doi field to resource models
- helper function for primary source look up

### Changes

- upgrade mex-model dependency to version 3
- make ruff linter config opt-out, instead of opt-in
- make instances of extracted data hashable
- BREAKING: Wikidata convenience function refactored and renamed to 'helper'
- wikidata helper function split between mex-common and mex-extractors
- code de-duplication: fixture extracted_primary_sources uses function-part of helper
- split up YearMonth and Year temporal types and improved patterns
- applied all changes to model fields according to model v3
- update LOINC pattern

### Fixed

- fix temporal entity schemas

## [0.38.0] - 2024-10-11

### Added

- add pattern constants for vocabs, emails, urls and ids to types module
- add regex pattern to json schema of identifier fields
- automatically add examples and useScheme to json schema of enum fields

### Changes

- BREAKING: use `identifier` instead of `stableTargetId` to get merged item from backend
- ensure identifier unions are typed to generic `Identifier` instead of the first match
  to signal that we don't actually know which of the union types is correct
- unify pydantic schema configuration for all types
- consistently parse emails, identifiers and temporals in models to their type, not str
- consistently serialize emails, ids and temporals in models to str, not their type
- make instances of Link type hashable, to harmonize them with Text models

### Removed

- drop manual examples from enum fields, because they are autogenerated now
- BREAKING: remove `MEX_ID_PATTERN` from types, in favor of `IDENTIFIER_PATTERN`
- BREAKING: make public `MEX_ID_ALPHABET` constant from identifier module private
- BREAKING: remove `__str__` methods from Text and Link classes
- BREAKING: drop support for parsing UUIDs as Identifiers, this was unused
- BREAKING: drop support for parsing Links from markdown syntax, this was unused
- BREAKING: remove pydantic1-style `validate` methods from all type models
- BREAKING: `BackendApiConnector.post_models` in favor of `post_extracted_items`

## [0.37.0] - 2024-10-01

### Added

- added methods for extracting persons by name or ID from ldap
- `contains_only_types` to check if fields are annotated as desired
- `group_fields_by_class_name` utility to simplify filtered model/field lookups
- new parameters to `get_inner_types` to customize what to unpack

## [0.36.1] - 2024-09-16

### Fixed

- pin pytz to 2024.1, as stopgap for MX-1703

## [0.36.0] - 2024-09-09

### Added

- added `BackendApiConnector` methods to cover all current (and near future) endpoints:
  `fetch_extracted_items`, `fetch_merged_items`, `get_merged_item`,
  `preview_merged_item` and `get_rule_set`
- complete the list of exported names in `models` and `types` modules

### Deprecated

- deprecated `BackendApiConnector.post_models` in favor of `post_extracted_items`

### Removed

- containerize section from release pipeline

### Fixed

- added the `rki/mex` user-agent to all requests of the HTTPConnector

## [0.35.0] - 2024-08-20

### Changes

- update cruft and loosen up pyproject dependencies
- harmonize signatures/docs of pydantic core/json schema manipulating methods

### Fixed

- fix schema tests not starting with diverging model names in common and mex-model
- fix serialization for temporal entity instances within pydantic models

## [0.34.0] - 2024-08-12

### Added

- wikidata fixtures to pytest plugin: wikidata_organization_raw, wikidata_organization,
  mocked_wikidata
- convenience function `get_merged_organization_id_by_query_with_extract_transform_and_load`
  for getting the stableTargetId of an organization, while transforming and loading the
  organization using the provided load function
- models for rule-set requests and responses along with typing and lookups
- add `BaseT` models to the exported names of `mex.common.models`
- add `MEX_ID_PATTERN` to the exported names of `mex.common.types`

### Changes

- move all base models and pydantic scaffolding into `mex.common.models.base`
  for a cleaner structure within the growing `models` module

## [0.33.0] - 2024-07-31

### Added

- HTTP connector backoff for 10 retries on 403 from server
- `rki/mex` user agent is sent with query requests via wikidata connector

### Changes

- changed backend api connector payload to "items"

- update wikidata search organization request query, with optional language parameter
  wikidata query search can be enhanced by specifying the language.
  EN is the default language.

## [0.32.0] - 2024-07-23

### Changes

- move log timestamp and coloring into the formatter

### Deprecated

- `mex.common.logging.echo` is deprecated in favor of `logging.info`

### Fixed

- add missing listyness-fix support for computed-fields

## [0.31.0] - 2024-07-17

### Removed

- BREAKING: ability to store different settings instances at the same time. Dependent
  repositories now must bundle all settings in a single class.

## [0.30.0] - 2024-07-16

### Added

- get count of found wikidata organizations

## [0.29.1] - 2024-07-15

## [0.29.0] - 2024-07-12

### Added

- add validator to base model that verifies computed fields can be set but not altered
- new class hierarchy for identifiers: ExtractedIdentifier and MergedIdentifier

### Changes

- improve typing for methods using `Self`
- make local type variables private
- use json instead of pickle to calculate checksum of models
- replace `set_identifiers` validator with computed fields on each extracted model

### Removed

- removed custom stringify method on base entities that included the `identifier` field

### Fixed

- fix typing for `__eq__` arguments

## [0.28.0] - 2024-07-08

### Added

- extract multiple organizations from wikidata

## [0.27.1] - 2024-06-14

### Changes

- update mex-model to version 2.5

## [0.27.0] - 2024-06-10

### Added

- add static class attribute `stemType` to models, containing an unprefixed entityType
- add `AnyRuleModel`, `RULE_MODEL_CLASSES`, `RULE_MODEL_CLASSES_BY_NAME` to models
- add type aliases `AnyPrimitiveType` and `LiteralStringType` to types
- add new utility function `ensure_postfix` for adding postfixes to strings

### Changes

- clean-up and unify `mapping` and `filter` class generation

## [0.26.1] - 2024-05-29

### Fixed

- fix memory identity provider seeding

## [0.26.0] - 2024-05-29

### Added

- add classes for Additive, Preventive and Subtractive rules for all entity types
- add types, lists and lookups for all three rule types to `mex.common.models`

### Changes

- move aux-extractor documentation from readme to `__init__` to have it in sphinx
- move `BaseModel` specific descriptions from class to model to avoid duplication
- BREAKING: move `FILTER_MODEL_BY_EXTRACTED_CLASS_NAME` to `mex.common.models`
- BREAKING: move `MAPPING_MODEL_BY_EXTRACTED_CLASS_NAME` to `mex.common.models`
- BREAKING: change `MEX_PRIMARY_SOURCE_IDENTIFIER` to end in `1`,
  so that it differs from `MEX_PRIMARY_SOURCE_STABLE_TARGET_ID`

## [0.25.1] - 2024-05-21

### Fixed

- isolate settings context before first test

## [0.25.0] - 2024-05-14

### Added

- add `precision` keyword to TemporalEntity constructor
- add transform function for single wikidata organization to extracted organization

### Changes

- add tests for ldap.extract

### Fixed

- fix ldap.extract.get_merged_ids_by_email

## [0.24.0] - 2024-04-12

### Added

- synchronize changes to fields in `BaseSettings` to all active settings subclasses
- added github action for renovatebot

### Changes

- make memory identity provider deterministic (same input args results in same
  stableTargetId and Identifier)
- rework `ContextStore` into `SingletonStore` with more intuitive API
- phase out ambiguous "context" naming in favor of more descriptive "singleton store"
- rename `SettingsContext` to `SETTINGS_STORE` and allow multiple active subclasses
- rename `ConnectorContext` to `CONNECTOR_STORE` removing its context manager functions
- replace `reset_connector_context()` with more consistent `CONNECTOR_STORE.reset()`

### Removed

- removed types `IdentifierT`, `SettingsType`, `ConnectorType` in favor of `typing.Self`
- remove github dependabot configuration

## [0.23.0] - 2024-04-08

### Changes

- return only one org from wikidata, if multiple or no org is found then return None
- filter quotation marks (") from requested wikidata label

## [0.22.0] - 2024-03-19

### Added

- port `get_inner_types` from `mex-backend` to `mex.common.utils`

### Changes

- rename Timestamp class to TemporalEntity
- added subclasses with specific resolution YearMonth, YearMonthDay, YearMonthDayTime
- modernize typing with syntactic sugar
- simplify `BaseModel._get_list_field_names` using `get_inner_types`
- switch from poetry to pdm
- use vocabulary JSON files from mex-model

### Removed

- remove vocabulary JSON files

### Fixed

- date and time validation working and harmonized with mex-model

## [0.21.0] - 2024-03-04

### Added

- add `entityType` type hint to `MExModel` (now `BaseEntity`)
- add types for `AnyBaseModel`, `AnyExtractedModel` and `AnyMergedModel`
- create more specific subclasses of `Identifier` (for extracted and merged)
- expose unions, lists and lookups for `Identifier` subclasses in `mex.common.types`

### Changes

- swap `contextvars.ContextVar` for `mex.common.context.ContextStore`
- move `stableTargetId` property from base models to extracted models
- update typing of identifiers to specific subclasses
- use `Annotated[..., Field(...)]` notation for pydantic field configs
- split up `mex.common.models.base` and move out `MExModel` and `JsonSchemaGenerator`
- rename `MExModel` to `BaseEntity` with only type hints an model config
- declare `hadPrimarySource`, `identifier` and `identifierInPrimarySource` as frozen

### Removed

- absorb unused `BaseExtractedData` into `ExtractedData`
- remove `stableTargetId` property from merged models
- drop support for sinks to accept merged items (now only for extracted data)

## [0.20.0] - 2024-02-22

### Changes

- update cruft and dev dependencies
- randomize test order by default

### Removed

- remove `mex.common.public_api` module and the correlating sinks
- remove `PathWrapper.resolve` and `PathWrapper.raw` methods

### Fixed

- remove `pytest.mark` from fixture in `mex.common.testing.plugin`

## [0.19.4] - 2024-02-15

### Changes

- update cruft and minor dependencies

### Removed

- date-time format validation for mapping model generation

## [0.19.3] - 2024-02-06

### Changes

- update cruft to apply new workflow trigger config
- update poetry and pre-commit dependencies

### Fixed

- fix mex mapping model name

## [0.19.2] - 2024-02-02

### Added

- pytest plugins for random order and parallelized test execution
- move dynamic mapping model generation from mex-assets

### Changes

- `mex.bat test` uses random order and xdist plugins by default

## [0.19.1] - 2024-01-19

### Added

- cruft template link
- workflow that syncs main branch to openCoDE
- constant for MEX_PRIMARY_SOURCE_IDENTIFIER

### Changes

- harmonized boilerplate

### Fixed

- ExtractedData raises proper ValidationError when parsing wrong base type

## [0.19.0] - 2024-01-12

### Added

- add `entityType` field in all extracted and merged models

### Fixed

- wikidata test

## [0.18.2] - 2024-01-11

### Added

- `CHANGELOG.md` documenting notable changes to this project
- a template for pull requests
- language french in language vocabulary

## [0.18.1] - 2024-01-03

### Added

- tests for `mex.common.types.PathWrapper`
- method `is_relative` to `mex.common.types.PathWrapper` to check whether the path is
  relative

### Changes

- resolve base paths of work/assets path fields in settings

### Fixed

- nesting of `mex.common.types.PathWrapper` on instantiation

## [0.18.0] - 2023-12-20

### Changes

- move `Sink` and `IdentityProvider` to `mex.common.types`

### Deprecated

- deprecate `MExModel.get_entity_type`, use `cls.__name__` instead
- deprecate `mex.common.models.MODEL_CLASSES[_BY_ENTITY_TYPE]`,
  use the more precise lists or dicts like `EXTRACTED_MODEL_CLASSES_BY_NAME` instead

## [0.17.1] - 2023-12-20

### Added

- use dmypy for pre-commit type checking

### Fixed

- fix previously undetected typing issue

### Changed

- configure CI linting to install poetry
- update versions
