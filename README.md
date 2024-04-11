# MEx common

Common library for MEx python projects.

[![cookiecutter](https://github.com/robert-koch-institut/mex-common/actions/workflows/cookiecutter.yml/badge.svg)](https://github.com/robert-koch-institut/mex-template)
[![cve-scan](https://github.com/robert-koch-institut/mex-common/actions/workflows/cve-scan.yml/badge.svg)](https://github.com/robert-koch-institut/mex-common/actions/workflows/cve-scan.yml)
[![documentation](https://github.com/robert-koch-institut/mex-common/actions/workflows/documentation.yml/badge.svg)](https://robert-koch-institut.github.io/mex-common)
[![linting](https://github.com/robert-koch-institut/mex-common/actions/workflows/linting.yml/badge.svg)](https://github.com/robert-koch-institut/mex-common/actions/workflows/linting.yml)
[![open-code](https://github.com/robert-koch-institut/mex-common/actions/workflows/open-code.yml/badge.svg)](https://gitlab.opencode.de/robert-koch-institut/mex/mex-common)
[![testing](https://github.com/robert-koch-institut/mex-common/actions/workflows/testing.yml/badge.svg)](https://github.com/robert-koch-institut/mex-common/actions/workflows/testing.yml)

## project

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
[project page](https://www.rki.de/DE/Content/Forsch/MEx/MEx_node.html).

[^1]: FAIR is referencing the so-called
[FAIR data principles](https://www.go-fair.org/fair-principles/) – guidelines to make
data Findable, Accessible, Interoperable and Reusable.

## package

The `mex-common` library is a software development toolkit that is used by multiple
components within the MEx project. It contains utilities for building pipelines like a
common commandline interface, logging and configuration setup. It also provides common
auxiliary connectors that can be used to fetch data from external services and a
re-usable implementation of the MEx metadata schema as pydantic models.

## license

This package is licensed under the [MIT license](/LICENSE). All other software
components of the MEx project are open-sourced under the same license as well.

## development

### installation

- on unix, consider using pyenv https://github.com/pyenv/pyenv
  - get pyenv `curl https://pyenv.run | bash`
  - install 3.11 `pyenv install 3.11`
  - switch version `pyenv global 3.11`
  - run `make install`
- on windows, consider using pyenv-win https://pyenv-win.github.io/pyenv-win/
  - follow https://pyenv-win.github.io/pyenv-win/#quick-start
  - install 3.11 `pyenv install 3.11`
  - switch version `pyenv global 3.11`
  - run `.\mex.bat install`

### linting and testing

- run all linters with `pdm lint`
- run only unit tests with `pdm unit`
- run unit and integration tests with `pdm test`

### updating dependencies

- update boilerplate files with `cruft update`
- update global requirements in `requirements.txt` manually
- update git hooks with `pre-commit autoupdate`
- update package dependencies using `pdm update-all`
- update github actions in `.github/workflows/*.yml` manually

### creating release

- update version in `pyproject.toml` and `CHANGELOG.md`
- commit update `git commit --message "..."`
- create a tag `git tag ...`
- push `git push --follow-tags`
