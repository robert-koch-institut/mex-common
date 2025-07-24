from typing import TYPE_CHECKING, Final

from mex.common.types import IdentityProvider

if TYPE_CHECKING:
    from mex.common.identity.base import BaseProvider

_PROVIDER_REGISTRY: Final[dict[IdentityProvider, type["BaseProvider"]]] = {}


def register_provider(
    key: IdentityProvider, provider_cls: type["BaseProvider"]
) -> None:
    """Register an implementation of an identity provider to a settings key.

    Args:
        key: Possible value of `BaseSettings.identity_provider`
        provider_cls: Implementation of an identity provider

    Raises:
        RuntimeError: When the `key` is already registered
    """
    if key in _PROVIDER_REGISTRY:
        msg = f"Already registered identity provider: {key}"
        raise RuntimeError(msg)
    _PROVIDER_REGISTRY[key] = provider_cls


def get_provider() -> "BaseProvider":
    """Get an instance of the identity provider as configured by `identity_provider`.

    Raises:
        RuntimeError: When the configured provider is not registered

    Returns:
        An instance of a subclass of `BaseProvider`
    """
    # break import cycle, sigh
    from mex.common.settings import BaseSettings  # noqa: PLC0415

    settings = BaseSettings.get()
    if settings.identity_provider in _PROVIDER_REGISTRY:
        provider_cls = _PROVIDER_REGISTRY[settings.identity_provider]
        return provider_cls.get()
    msg = f"Identity provider not implemented: {settings.identity_provider}"
    raise RuntimeError(msg)
