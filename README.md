# MEx common

Common library for MEx python projects.

[![testing](https://github.com/robert-koch-institut/mex-common/actions/workflows/testing.yml/badge.svg)](https://github.com/robert-koch-institut/mex-common/actions/workflows/testing.yml)
[![linting](https://github.com/robert-koch-institut/mex-common/actions/workflows/linting.yml/badge.svg)](https://github.com/robert-koch-institut/mex-common/actions/workflows/linting.yml)
[![cve-scan](https://github.com/robert-koch-institut/mex-common/actions/workflows/cve-scan.yml/badge.svg)](https://github.com/robert-koch-institut/mex-common/actions/workflows/cve-scan.yml)
[![documentation](https://github.com/robert-koch-institut/mex-common/actions/workflows/documentation.yml/badge.svg)](https://robert-koch-institut.github.io/mex-common)

## project

With the Metadata Exchange (MEx) project, the [RKI](https://www.rki.de) is developing a
transparency platform for finding metadata on the institute's research activities and
data.

MEx makes metadata findable, accessible, and shareable on a daily basis,
as well as available for further research. MEx enables users to get an overview of what
research data is available, understand its context, and know what needs to be considered
for subsequent use.

The platform is currently in internal use but will also be made publicly available
and thus be available to external researchers as well as the interested (professional)
public.

For further details, please consult the
[project page](https://www.rki.de/DE/Content/Forsch/MEx/MEx_node.html).

## package

The `mex-common` library is a software development toolkit that is used by multiple
components within the MEx project. It contains utilities for building pipelines
like a common commandline interface, logging and configuration setup. It also provides
common auxiliary connectors that can be used to fetch data from external services and
a re-usable implementation of the MEx metadata schema as pydantic models.

## license

This package is licensed under the [MIT license](/LICENSE). Other components of the
MEx project will be released under the same license in the future.

## development

### installation

- on unix, consider using pyenv https://github.com/pyenv/pyenv
  - get pyenv `curl https://pyenv.run | bash`
  - install 3.11 `pyenv install 3.11`
  - create env `pyenv virtualenv 3.11 mex`
  - go to repo root
  - use env `pyenv local mex`
  - run `make install`
- on windows, see https://python-poetry.org/docs/managing-environments
  - install `python3.11` in your preferred way
  - go to repo root
  - run `.\mex.bat install`

### linting and testing

- on unix run `make test`
- on windows run `.\mex.bat test`
- or run manually
  - linter checks via `pre-commit run --all-files`
  - all tests via `poetry run pytest`

### updating dependencies

- update global dependencies in `requirements.txt` manually
- show outdated dependencies with `poetry show --outdated`
- update dependencies in poetry using `poetry update --lock`
- update github actions manually in `.github\workflows\default.yml`
