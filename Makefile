.PHONY: all test setup hooks install linter pytest wheel docs
all: install test
test: linter pytest

setup:
	# install meta requirements system-wide
	@ echo installing requirements; \
	python -m pip --quiet --disable-pip-version-check install --force-reinstall -r requirements.txt; \

hooks:
	# install pre-commit hooks when not in CI
	@ if [ -z "$$CI" ]; then \
		pre-commit install; \
	fi; \

install: setup hooks
	# install packages from lock file in local virtual environment
	@ echo installing package; \
	pdm sync --clean --group dev; \

linter:
	# run the linter hooks from pre-commit on all files
	@ echo linting all files; \
	pre-commit run --all-files; \

pytest:
	# run the pytest test suite with all unit tests
	@ echo running unit tests; \
	poetry run pytest -m "not integration"; \

wheel:
	# build the python package
	@ echo building wheel; \
	poetry build --no-interaction --format wheel; \

docs:
	# use sphinx to auto-generate html docs from code
	@ echo generating api docs; \
	pdm run sphinx-apidoc -f -o docs/source mex; \
	pdm run sphinx-build -aE -b dirhtml docs docs/dist; \
