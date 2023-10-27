from typing import Final, Hashable

from mex.common.identity.base import BaseProvider
from mex.common.identity.dummy import DummyIdentityProvider
from mex.common.identity.types import IdentityProvider

_PROVIDER_REGISTRY: Final[dict[Hashable, type[BaseProvider]]] = {}


def register_provider(key: Hashable, provider_cls: type[BaseProvider]) -> None:
    """Register an implementation of an identity provider to a settings key.

    Args:
        key: Possible value of `Settings.identity_provider`, this will be of type
            `mex.common.identity.types.IdentityProvider` on the `BaseSettings`
            but maybe overwritten in other packages that have their own settings
        provider_cls: Implementation of an identity provider

    Raises:
        RuntimeError: When the `key` is already registered
    """
    if key in _PROVIDER_REGISTRY:
        raise RuntimeError(f"Already registered identity provider: {key}")
    _PROVIDER_REGISTRY[key] = provider_cls


def get_provider() -> BaseProvider:
    """Get an instance of the identity provider as configured by `identity_provider`.

    Raises:
        RuntimeError: When the configured provider is not registered

    Returns:
        An instance of a subclass of `BaseProvider`
    """
    # break import cycle, sigh
    from mex.common.settings import BaseSettings

    settings = BaseSettings.get()
    if settings.identity_provider in _PROVIDER_REGISTRY:
        provider_cls = _PROVIDER_REGISTRY[settings.identity_provider]
        return provider_cls.get()
    raise RuntimeError(
        f"Identity provider not implemented: {settings.identity_provider}"
    )


# register the default providers shipped with mex-common
register_provider(IdentityProvider.DUMMY, DummyIdentityProvider)
