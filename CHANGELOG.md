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
- prepare switch from poetry to pdm

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
