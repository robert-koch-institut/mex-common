from enum import Enum

import pytest
from pytest import MonkeyPatch

from mex.common.assets.base import BaseAssetsConnector
from mex.common.assets.filesystem import FilesystemAssetsConnector
from mex.common.assets.registry import (
    _CONNECTOR_REGISTRY,
    get_assets_connector,
    register_assets_connector,
)
from mex.common.settings import SETTINGS_STORE, BaseSettings
from mex.common.types import AssetsConnectorType


class DummyAssetsConnectorType(Enum):
    DUMMY = "dummy"


class DummyAssetsConnector(BaseAssetsConnector):
    def __init__(self) -> None:
        pass

    def read(self, _path: str) -> bytes:  # pragma: no cover
        raise RuntimeError

    def glob(self, _path: str, _pattern: str) -> list[str]:  # pragma: no cover
        raise RuntimeError

    def close(self) -> None:
        pass


class DummySettings(BaseSettings):
    assets_connector: AssetsConnectorType | DummyAssetsConnectorType = (
        AssetsConnectorType.FILESYSTEM  # type: ignore[assignment]
    )


def test_register_assets_connector_error() -> None:
    with pytest.raises(RuntimeError, match="Already registered"):
        register_assets_connector(
            AssetsConnectorType.FILESYSTEM, FilesystemAssetsConnector
        )


def test_register_assets_connector() -> None:
    register_assets_connector(DummyAssetsConnectorType.DUMMY, DummyAssetsConnector)  # type: ignore[arg-type]

    assert _CONNECTOR_REGISTRY[DummyAssetsConnectorType.DUMMY] == DummyAssetsConnector  # type: ignore[index]


def test_get_assets_connector_error(monkeypatch: MonkeyPatch) -> None:
    # first remove the default provider from the registry
    monkeypatch.delitem(_CONNECTOR_REGISTRY, AssetsConnectorType.FILESYSTEM)

    # then get an error when we try to get an instance
    with pytest.raises(RuntimeError, match="not implemented"):
        get_assets_connector()


def test_get_assets_connector() -> None:
    SETTINGS_STORE.reset()
    settings = DummySettings.get()
    settings.assets_connector = DummyAssetsConnectorType.DUMMY

    register_assets_connector(DummyAssetsConnectorType.DUMMY, DummyAssetsConnector)  # type: ignore[arg-type]

    provider = get_assets_connector()
    assert isinstance(provider, DummyAssetsConnector)
