@echo off

set target=%1

if "%target%"=="install" goto install
if "%target%"=="lint" goto lint
if "%target%"=="unit" goto unit
if "%target%"=="test" goto test
if "%target%"=="docs" goto docs
echo invalid argument %target%
exit /b 1


:install
@REM install meta requirements system-wide
echo installing requirements
pip --disable-pip-version-check install --force-reinstall -r requirements.txt
if %errorlevel% neq 0 exit /b %errorlevel%

@REM install pre-commit hooks when not in CI
if "%CI%"=="" (
    pre-commit install
    if %errorlevel% neq 0 exit /b %errorlevel%
)

@REM install packages from lock file in local virtual environment
echo installing package
uv sync
exit /b %errorlevel%


:lint
@REM run the linter hooks from pre-commit on all files
echo linting all files
pre-commit run --all-files
exit /b %errorlevel%


:unit
@REM run the test suite with all unit tests
echo running unit tests
uv run pytest -m "not integration"
exit /b %errorlevel%


:test
@REM run the unit and integration test suites
echo running all tests
uv run pytest --numprocesses=auto --dist=worksteal
exit /b %errorlevel%


:docs
@REM use sphinx to auto-generate html docs from code
echo generating docs
uv run sphinx-apidoc -f -o docs/source mex
uv run sphinx-build -aE -b dirhtml docs docs/dist
exit /b %errorlevel%
