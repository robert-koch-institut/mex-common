from typing import TYPE_CHECKING, Final

from mex.common.types import AssetsConnectorType

if TYPE_CHECKING:
    from .base import BaseAssetsConnector

_CONNECTOR_REGISTRY: Final[dict[AssetsConnectorType, type["BaseAssetsConnector"]]] = {}

def register_assets_connector(
    key: AssetsConnectorType, connector_cls: type["BaseAssetsConnector"]
) -> None:
    """Register an implementation of an assets connector to a settings key.

    Args:
        key: Possible value of `BaseSettings.assets_connector`
        connector_cls: Implementation of an assets connector

    Raises:
        RuntimeError: When the `key` is already registered
    """
    if key in _CONNECTOR_REGISTRY:
        msg = f"Already registered assets connector: {key}"
        raise RuntimeError(msg)
    _CONNECTOR_REGISTRY[key] = connector_cls

def get_assets_connector() -> "BaseAssetsConnector":
    """Get an instance of the assets connector as configured by `assets_connector`.

    Raises:
        RuntimeError: When the configured connector is not registered

    Returns:
        An instance of a subclass of `BaseAssetsConnector`
    """
    # break import cycle, sigh
    from mex.common.settings import BaseSettings  # noqa: PLC0415

    settings = BaseSettings.get()
    if settings.assets_connector in _CONNECTOR_REGISTRY:
        connector_cls = _CONNECTOR_REGISTRY[settings.assets_connector]
        return connector_cls.get()
    msg = f"Assets connector not implemented: {settings.assets_connector}"
    raise RuntimeError(msg)