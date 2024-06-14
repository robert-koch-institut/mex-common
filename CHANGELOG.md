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
