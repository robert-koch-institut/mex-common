# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changes

- move `Sink` and `IdentityProvider` to `mex.common.types`

### Deprecated

- deprecate `MExModel.get_entity_type`, use `cls.__name__` instead
- deprecate `mex.common.models.MODEL_CLASSES[_BY_ENTITY_TYPE]`, use the more precise lists or dicts like `EXTRACTED_MODEL_CLASSES_BY_NAME` instead

### Removed

### Fixed

### Security

## [0.17.1] - 2023-12-20

### Added

- use dmypy for pre-commit type checking

### Fixed

- fix previously undetected typing issue

### Changed

- configure CI linting to install poetry
- update versions
