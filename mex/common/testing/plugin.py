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

import pytest
import requests
from langdetect import DetectorFactory
from pydantic import AnyUrl
from requests import HTTPError, Response

from mex.common.connector import CONNECTOR_STORE
from mex.common.models import ExtractedPrimarySource
from mex.common.orcid.connector import OrcidConnector
from mex.common.primary_source.helpers import get_all_extracted_primary_sources
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
def isolate_work_dir(tmp_path: Path, settings: BaseSettings) -> None:
    """Set settings.work_dir variable to a temp path for all tests."""
    settings.work_dir = tmp_path


@pytest.fixture(autouse=True)
def settings() -> BaseSettings:
    """Load the settings for this pytest session."""
    return BaseSettings.get()


@pytest.fixture(autouse=True)
def isolate_settings(
    isolate_assets_dir: None,  # noqa: ARG001
    isolate_work_dir: None,  # noqa: ARG001
) -> Generator[None, None, None]:
    """Automatically reset the settings singleton store."""
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
    return get_all_extracted_primary_sources()


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
        _self: WikidataQueryServiceConnector, _query: str
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
        _self: WikidataAPIConnector, _item_id: str
    ) -> dict[str, str]:
        return wikidata_organization_raw

    monkeypatch.setattr(
        WikidataAPIConnector,
        "get_wikidata_item_details_by_id",
        get_wikidata_item_details_by_id,
    )


@pytest.fixture
def orcid_person_raw() -> dict[str, Any]:
    """Return a raw orcid person."""
    with open(Path(__file__).parent / "test_data" / "orcid_person_raw.json") as fh:
        return cast(dict[str, Any], json.load(fh))


@pytest.fixture
def orcid_person_jayne_raw() -> dict[str, Any]:
    """Return a raw orcid person."""
    with open(
        Path(__file__).parent / "test_data" / "orcid_person_jayne_raw.json"
    ) as fh:
        return cast(dict[str, Any], json.load(fh))


@pytest.fixture
def orcid_multiple_matches() -> dict[str, Any]:
    """Return a raw orcid person."""
    with open(
        Path(__file__).parent / "test_data" / "orcid_multiple_matches.json"
    ) as fh:
        return cast(dict[str, Any], json.load(fh))


@pytest.fixture
def mocked_orcid(
    monkeypatch: pytest.MonkeyPatch,
    orcid_person_raw: dict[str, Any],
    orcid_multiple_matches: dict[str, Any],
    orcid_person_jayne_raw: dict[str, Any],
) -> None:
    """Mock orcid connector."""
    response_query = Mock(spec=Response, status_code=200)

    session = MagicMock(spec=requests.Session)
    session.get = MagicMock(side_effect=[response_query])

    def mocked_init(self: OrcidConnector) -> None:
        self.session = session

    monkeypatch.setattr(OrcidConnector, "__init__", mocked_init)

    def fetch(_self: OrcidConnector, filters: dict[str, Any]) -> dict[str, Any]:
        if filters.get("given-names") == "John":
            return {"num-found": 1, "result": [orcid_person_raw]}
        if filters.get("given-and-family-names") == '"Jayne Carberry"':
            return {"num-found": 1, "result": [orcid_person_jayne_raw]}
        if (
            filters.get("given-names") == "Multiple"
            or filters.get("given-and-family-names") == "Jayne Carberry"
        ):
            return orcid_multiple_matches
        return {"result": [], "num-found": 0}

    monkeypatch.setattr(OrcidConnector, "fetch", fetch)

    def get_data_by_id(_self: OrcidConnector, orcid_id: str) -> dict[str, Any]:
        if orcid_id == "0009-0004-3041-5706":
            return orcid_person_raw
        if orcid_id == "0000-0003-4634-4047":
            return orcid_person_jayne_raw
        msg = "404 Not Found"
        raise HTTPError(msg)

    monkeypatch.setattr(OrcidConnector, "get_data_by_id", get_data_by_id)
