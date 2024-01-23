@echo off

set target=%1

if "%target%"=="install" goto install
if "%target%"=="test" goto test
if "%target%"=="docs" goto docs
echo invalid argument %target%
exit /b 1


:install
@REM install meta requirements system-wide
Python -m pip --quiet --disable-pip-version-check install --force-reinstall -r requirements.txt
if %errorlevel% neq 0 exit /b %errorlevel%

@REM install pre-commit hooks when not in CI
if "%CI%"=="" (
    pre-commit install
    if %errorlevel% neq 0 exit /b %errorlevel%
)

@REM run the poetry installation with embedded virtual environment
echo installing package
poetry install --no-interaction --sync
exit /b %errorlevel%


:test
@REM run the linter hooks from pre-commit on all files
echo linting all files
pre-commit run --all-files
if %errorlevel% neq 0 exit /b %errorlevel%

@REM run the pytest test suite with unit and integration tests in random order
@REM distributed across all available CPU cores
echo running all tests
poetry run pytest --random-order-bucket=global --numprocesses=auto --dist=worksteal
exit /b %errorlevel%


:docs
@REM use sphinx to auto-generate html docs from code
echo generating api docs
poetry run sphinx-apidoc -f -o docs\source mex
if %errorlevel% neq 0 exit /b %errorlevel%
poetry run sphinx-build -aE -b dirhtml docs docs\dist
exit /b %errorlevel%
