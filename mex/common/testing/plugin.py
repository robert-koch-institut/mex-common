"""Pytest plugin with common MEx-specific fixtures.

Activate by adding `pytest_plugins = ("mex.common.testing.plugin",)`
to the `conftest.py` in your root test folder.
"""

import os
from enum import Enum
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock

from langdetect import DetectorFactory
from pydantic import AnyUrl

from mex.common.connector import reset_connector_context
from mex.common.models import ExtractedPrimarySource
from mex.common.primary_source.extract import extract_seed_primary_sources
from mex.common.primary_source.transform import (
    transform_seed_primary_sources_to_extracted_primary_sources,
)
from mex.common.settings import BaseSettings, SettingsContext


class NoOpPytest:
    """No-op pytest drop-in for when dev dependencies are not installed."""

    FixtureRequest = Any
    MonkeyPatch = Any
    fixture = MagicMock()


try:
    import pytest
except ImportError:
    pytest = NoOpPytest  # type: ignore[assignment]


@pytest.fixture(autouse=True)
def patch_reprs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow for easier copying of expected output by patching __repr__ methods."""
    monkeypatch.setattr(
        Enum, "__repr__", lambda self: f"{self.__class__.__name__}.{self.name}"
    )
    monkeypatch.setattr(
        AnyUrl, "__repr__", lambda self: f'AnyUrl("{self}", scheme="{self.scheme}")'
    )


@pytest.fixture(autouse=True)
def isolate_assets_dir(
    is_integration_test: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Disable the `MEX_ASSETS_DIR` environment variable for unit testing."""
    if not is_integration_test:  # pragma: no cover
        monkeypatch.delenv("MEX_ASSETS_DIR", raising=False)


@pytest.fixture(autouse=True)
def isolate_work_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Set the `MEX_WORK_DIR` environment variable to a temp path for all tests."""
    monkeypatch.setenv("MEX_WORK_DIR", str(tmp_path))


@pytest.fixture(autouse=True)
def settings() -> BaseSettings:
    """Load the settings for this pytest session."""
    return BaseSettings.get()


@pytest.fixture(autouse=True)
def isolate_settings_context() -> Generator[None, None, None]:
    """Automatically reset the settings context variable."""
    yield
    SettingsContext.set(None)


@pytest.fixture(autouse=True)
def isolate_connector_context() -> Generator[None, None, None]:
    """Automatically close all connectors and remove from context variable."""
    yield
    reset_connector_context()


@pytest.fixture()
def is_integration_test(request: pytest.FixtureRequest) -> bool:
    """Check the markers of a test to see if this is an integration test."""
    return any(m.name == "integration" for m in request.keywords.get("pytestmark", ()))


@pytest.fixture()
def in_continuous_integration() -> bool:
    """Check the environment variable `CI` to determine whether we are in CI."""
    return os.environ.get("CI") == "true"


@pytest.fixture(autouse=True)
def isolate_langdetect() -> None:
    """Automatically set the language detection seed to a stable value during tests."""
    DetectorFactory.seed = 0


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale() -> list[str]:
    """Configure the default locales used for localizing fake data."""
    return ["de_DE", "en_US"]


@pytest.fixture()
def extracted_primary_sources() -> dict[str, ExtractedPrimarySource]:
    """Return a mapping from `identifierInPrimarySource` to ExtractedPrimarySources."""
    seed_primary_sources = extract_seed_primary_sources()
    extracted_primary_sources = (
        transform_seed_primary_sources_to_extracted_primary_sources(
            seed_primary_sources
        )
    )
    return {p.identifierInPrimarySource: p for p in extracted_primary_sources}
