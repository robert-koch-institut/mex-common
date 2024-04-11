@echo off

set target=%1

if "%target%"=="install" goto install
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
pdm install-all
exit /b %errorlevel%


:test
@REM run the linter hooks from pre-commit on all files
echo linting all files
pdm lint
if %errorlevel% neq 0 exit /b %errorlevel%

@REM run the pytest test suite with unit and integration tests
echo running all tests
pdm test
exit /b %errorlevel%


:docs
@REM use sphinx to auto-generate html docs from code
echo generating docs
pdm doc
exit /b %errorlevel%
