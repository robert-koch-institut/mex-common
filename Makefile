.PHONY: all test setup hooks install linter pytest wheel docs
all: install test
test: linter pytest

LATEST = $(shell git describe --tags $(shell git rev-list --tags --max-count=1))
PWD = $(shell pwd)

setup:
	# install meta requirements system-wide
	@ echo installing requirements; \
	pip --disable-pip-version-check install --force-reinstall -r requirements.txt; \

hooks:
	# install pre-commit hooks when not in CI
	@ if [ -z "$$CI" ]; then \
		pre-commit install; \
	fi; \

install: setup hooks
	# install packages from lock file in local virtual environment
	@ echo installing package; \
	pdm install-all; \

linter:
	# run the linter hooks from pre-commit on all files
	@ echo linting all files; \
	pdm lint; \

pytest:
	# run the pytest test suite with all unit tests
	@ echo running unit tests; \
	pdm unit; \

wheel:
	# build the python package
	@ echo building wheel; \
	pdm wheel; \

docs:
	# use sphinx to auto-generate html docs from code
	@ echo generating docs; \
	pdm doc; \
