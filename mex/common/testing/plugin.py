"""Pytest plugin with common MEx-specific fixtures.

Activate by adding `pytest_plugins = ("mex.common.testing.plugin",)`
to the `conftest.py` in your root test folder.
"""

import json
import os
import re
from collections.abc import Generator
from enum import Enum
from pathlib import Path
from typing import Any, cast
from unittest.mock import MagicMock, Mock

import requests
from langdetect import DetectorFactory
from pydantic import AnyUrl
from requests import HTTPError, Response

from mex.common.connector import CONNECTOR_STORE
from mex.common.models import ExtractedPrimarySource
from mex.common.orcid.connector import OrcidConnector
from mex.common.orcid.models import OrcidRecord, OrcidSearchResponse
from mex.common.primary_source.extract import extract_seed_primary_sources
from mex.common.primary_source.transform import (
    transform_seed_primary_sources_to_extracted_primary_sources,
)
from mex.common.settings import SETTINGS_STORE, BaseSettings
from mex.common.wikidata.connector import WikidataAPIConnector
from mex.common.wikidata.models import WikidataOrganization


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
    is_integration_test: bool,  # noqa: FBT001
    monkeypatch: pytest.MonkeyPatch,
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
    isolate_assets_dir: None,  # noqa: ARG001
    isolate_work_dir: None,  # noqa: ARG001
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
    with (
        Path(__file__).parent / "test_data" / "wikidata_organization_raw.json"
    ).open() as fh:
        return cast("dict[str, Any]", json.load(fh))


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

    def mocked_init(self: WikidataAPIConnector) -> None:
        self.session = session

    monkeypatch.setattr(WikidataAPIConnector, "__init__", mocked_init)

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
    with (Path(__file__).parent / "test_data" / "orcid_person_raw.json").open() as fh:
        return cast("dict[str, Any]", json.load(fh))


@pytest.fixture
def orcid_person_jayne_raw() -> dict[str, Any]:
    """Return a raw orcid person."""
    with (
        Path(__file__).parent / "test_data" / "orcid_person_jayne_raw.json"
    ).open() as fh:
        return cast("dict[str, Any]", json.load(fh))


@pytest.fixture
def orcid_multiple_matches() -> dict[str, Any]:
    """Return a raw orcid person."""
    with (
        Path(__file__).parent / "test_data" / "orcid_multiple_matches.json"
    ).open() as fh:
        return cast("dict[str, Any]", json.load(fh))


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

    def search_records_by_name(  # noqa: PLR0913
        _self: OrcidConnector,
        given_names: str | None = None,
        family_name: str | None = None,  # noqa: ARG001
        given_and_family_names: str | None = None,
        filters: dict[str, Any] | None = None,  # noqa: ARG001
        skip: int = 0,  # noqa: ARG001
        limit: int = 10,  # noqa: ARG001
    ) -> OrcidSearchResponse:
        response = {"result": [], "num-found": 0}
        if given_names == "John":
            response = {"num-found": 1, "result": [orcid_person_raw]}
        elif given_and_family_names == "Jayne Carberry":
            response = {"num-found": 1, "result": [orcid_person_jayne_raw]}
        elif given_names == "Multiple" or given_and_family_names == "Multiple Carberry":
            response = orcid_multiple_matches
        return OrcidSearchResponse.model_validate(response)

    monkeypatch.setattr(
        OrcidConnector, "search_records_by_name", search_records_by_name
    )

    def get_record_by_id(
        _self: OrcidConnector,
        orcid_id: str,
    ) -> OrcidRecord:
        if orcid_id == "0009-0004-3041-5706":
            return OrcidRecord.model_validate(orcid_person_raw)
        if re.match(
            r"^[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}$", orcid_id
        ):
            return OrcidRecord.model_validate(orcid_person_jayne_raw)
        msg = "404 Not Found"
        raise HTTPError(msg)

    monkeypatch.setattr(OrcidConnector, "get_record_by_id", get_record_by_id)
