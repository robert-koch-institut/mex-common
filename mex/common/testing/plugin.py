"""Pytest plugin with common MEx-specific fixtures.

Activate by adding `pytest_plugins = ("mex.common.testing.plugin",)`
to the `conftest.py` in your root test folder.
"""

import json
import os
from collections.abc import Generator
from enum import Enum
from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock, Mock

import requests
from langdetect import DetectorFactory
from pydantic import AnyUrl
from requests import Response

from mex.common.connector import CONNECTOR_STORE
from mex.common.models import ExtractedPrimarySource
from mex.common.primary_source.extract import extract_seed_primary_sources
from mex.common.primary_source.transform import (
    transform_seed_primary_sources_to_extracted_primary_sources,
)
from mex.common.settings import SETTINGS_STORE, BaseSettings
from mex.common.wikidata.connector import (
    WikidataAPIConnector,
    WikidataQueryServiceConnector,
)
from mex.common.wikidata.models.organization import WikidataOrganization


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
def isolate_settings(
    isolate_assets_dir: None, isolate_work_dir: None
) -> Generator[None, None, None]:
    """Automatically reset the settings singleton store."""
    SETTINGS_STORE.reset()
    yield
    SETTINGS_STORE.reset()


@pytest.fixture(autouse=True)
def isolate_connectors() -> Generator[None, None, None]:
    """Automatically close all connectors and remove from singleton store."""
    yield
    CONNECTOR_STORE.reset()


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


@pytest.fixture
def wikidata_organization_raw() -> dict[str, Any]:
    """Return a raw wikidata organization."""
    with open(
        Path(__file__).parent / "test_data" / "wikidata_organization_raw.json"
    ) as fh:
        return cast(dict[str, Any], json.load(fh))


@pytest.fixture
def wikidata_organization(
    wikidata_organization_raw: dict[str, Any],
) -> WikidataOrganization:
    """Return a wikidata organization instance."""
    return WikidataOrganization.model_validate(wikidata_organization_raw)


@pytest.fixture
def mocked_wikidata(
    monkeypatch: pytest.MonkeyPatch, wikidata_organization_raw: dict[str, Any]
) -> None:
    """Mock wikidata connector."""
    response_query = Mock(spec=Response, status_code=200)

    session = MagicMock(spec=requests.Session)
    session.get = MagicMock(side_effect=[response_query])

    def mocked_init(self: WikidataQueryServiceConnector) -> None:
        self.session = session

    monkeypatch.setattr(WikidataQueryServiceConnector, "__init__", mocked_init)
    monkeypatch.setattr(WikidataAPIConnector, "__init__", mocked_init)

    # mock search_wikidata_with_query

    def get_data_by_query(
        self: WikidataQueryServiceConnector, query: str
    ) -> list[dict[str, dict[str, str]]]:
        return [
            {
                "item": {
                    "type": "uri",
                    "value": "http://www.wikidata.org/entity/Q26678",
                },
                "itemLabel": {"xml:lang": "en", "type": "literal", "value": "BMW"},
                "itemDescription": {
                    "xml:lang": "en",
                    "type": "literal",
                    "value": "German automotive manufacturer, and conglomerate",
                },
            },
        ]

    monkeypatch.setattr(
        WikidataQueryServiceConnector, "get_data_by_query", get_data_by_query
    )

    # mock get_wikidata_org_with_org_id

    def get_wikidata_item_details_by_id(
        self: WikidataAPIConnector, item_id: str
    ) -> dict[str, str]:
        return wikidata_organization_raw

    monkeypatch.setattr(
        WikidataAPIConnector,
        "get_wikidata_item_details_by_id",
        get_wikidata_item_details_by_id,
    )
