from collections.abc import Generator

import pytest

from mex.common.assets import FilesystemAssetsConnector, register_assets_connector
from mex.common.assets.registry import _CONNECTOR_REGISTRY
from mex.common.types.assets import AssetsConnectorType


@pytest.fixture(autouse=True)
def isolate_assets_connector_registry() -> Generator[None, None, None]:
    """Restore the assets_connector registry after each identity test."""
    yield
    _CONNECTOR_REGISTRY.clear()
    register_assets_connector(AssetsConnectorType.FILESYSTEM, FilesystemAssetsConnector)
