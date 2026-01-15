.PHONY: all test setup hooks install lint test wheel docs
all: install lint test

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
	uv sync; \

lint:
	# run the linter hooks from pre-commit on all files
	@ echo linting all files; \
	pre-commit run --all-files; \

unit:
	# run the test suite with all unit tests
	@ echo running unit tests; \
	pdm run pytest -m 'not integration'; \

test:
	# run the unit and integration test suites
	@ echo running all tests; \
	pdm run pytest --numprocesses=auto --dist=worksteal; \

wheel:
	# build the python package
	@ echo building wheel; \
	pdm build --no-sdist; \

docs:
	# use sphinx to auto-generate html docs from code
	@ echo generating docs; \
	uv run sphinx-apidoc -f -o docs/source mex; \
	uv run sphinx-build -aE -b dirhtml docs docs/dist; \
