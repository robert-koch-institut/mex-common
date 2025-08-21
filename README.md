# MEx common

Common library for MEx python projects.

[![cookiecutter](https://github.com/robert-koch-institut/mex-common/actions/workflows/cookiecutter.yml/badge.svg)](https://github.com/robert-koch-institut/mex-template)
[![cve-scan](https://github.com/robert-koch-institut/mex-common/actions/workflows/cve-scan.yml/badge.svg)](https://github.com/robert-koch-institut/mex-common/actions/workflows/cve-scan.yml)
[![documentation](https://github.com/robert-koch-institut/mex-common/actions/workflows/documentation.yml/badge.svg)](https://robert-koch-institut.github.io/mex-common)
[![linting](https://github.com/robert-koch-institut/mex-common/actions/workflows/linting.yml/badge.svg)](https://github.com/robert-koch-institut/mex-common/actions/workflows/linting.yml)
[![open-code](https://github.com/robert-koch-institut/mex-common/actions/workflows/open-code.yml/badge.svg)](https://gitlab.opencode.de/robert-koch-institut/mex/mex-common)
[![testing](https://github.com/robert-koch-institut/mex-common/actions/workflows/testing.yml/badge.svg)](https://github.com/robert-koch-institut/mex-common/actions/workflows/testing.yml)

## Project

The Metadata Exchange (MEx) project is committed to improve the retrieval of RKI
research data and projects. How? By focusing on metadata: instead of providing the
actual research data directly, the MEx metadata catalog captures descriptive information
about research data and activities. On this basis, we want to make the data FAIR[^1] so
that it can be shared with others.

Via MEx, metadata will be made findable, accessible and shareable, as well as available
for further research. The goal is to get an overview of what research data is available,
understand its context, and know what needs to be considered for subsequent use.

RKI cooperated with D4L data4life gGmbH for a pilot phase where the vision of a
FAIR metadata catalog was explored and concepts and prototypes were developed.
The partnership has ended with the successful conclusion of the pilot phase.

After an internal launch, the metadata will also be made publicly available and thus be
available to external researchers as well as the interested (professional) public to
find research data from the RKI.

For further details, please consult our
[project page](https://www.rki.de/DE/Aktuelles/Publikationen/Forschungsdaten/MEx/metadata-exchange-plattform-mex-node.html).

[^1]: FAIR is referencing the so-called
[FAIR data principles](https://www.go-fair.org/fair-principles/) – guidelines to make
data Findable, Accessible, Interoperable and Reusable.

**Contact** \
For more information, please feel free to email us at [mex@rki.de](mailto:mex@rki.de).

### Publisher

**Robert Koch-Institut** \
Nordufer 20 \
13353 Berlin \
Germany

## Package

The `mex-common` library is a software development toolkit that is used by multiple
components within the MEx project. It contains utilities for building pipelines like a
common commandline interface, logging and configuration setup. It also provides common
auxiliary connectors that can be used to fetch data from external services and a
re-usable implementation of the MEx metadata schema as pydantic models.

## License

This package is licensed under the [MIT license](/LICENSE). All other software
components of the MEx project are open-sourced under the same license as well.

## Development

### Installation

- install python3.11 on your system
- on unix, run `make install`
- on windows, run `.\mex.bat install`

### Linting and testing

- run all linters with `make lint` or `.\mex.bat lint`
- run unit and integration tests with `make test` or `.\mex.bat test`
- run just the unit tests with `make unit` or `.\mex.bat unit`

### Updating dependencies

- update boilerplate files with `cruft update`
- update global requirements in `requirements.txt` manually
- update git hooks with `pre-commit autoupdate`
- update package dependencies using `pdm update-all`
- update github actions in `.github/workflows/*.yml` manually

### Creating release

- run `pdm release RULE` to release a new version where RULE determines which part of
  the version to update and is one of `major`, `minor`, `patch`.
