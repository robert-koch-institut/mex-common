from enum import Enum

import pytest
from pytest import MonkeyPatch

from mex.common.identity.base import BaseProvider
from mex.common.identity.memory import MemoryIdentityProvider
from mex.common.identity.models import Identity
from mex.common.identity.registry import (
    _PROVIDER_REGISTRY,
    get_provider,
    register_provider,
)
from mex.common.settings import SETTINGS_STORE, BaseSettings
from mex.common.types import IdentityProvider


class DummyIdentityProvider(Enum):
    DUMMY = "dummy"


class DummyProvider(BaseProvider):
    def __init__(self) -> None:
        pass

    def assign(self, *_: str) -> Identity:  # pragma: no cover
        raise RuntimeError

    def fetch(self, **_: str | None) -> list[Identity]:  # pragma: no cover
        raise RuntimeError

    def close(self) -> None:
        pass


class DummySettings(BaseSettings):
    identity_provider: IdentityProvider | DummyIdentityProvider = (
        IdentityProvider.MEMORY  # type: ignore[assignment]
    )


def test_register_provider_error() -> None:
    with pytest.raises(RuntimeError, match="Already registered identity provider"):
        register_provider(IdentityProvider.MEMORY, MemoryIdentityProvider)


def test_register_provider() -> None:
    register_provider(DummyIdentityProvider.DUMMY, DummyProvider)  # type: ignore[arg-type]

    assert _PROVIDER_REGISTRY[DummyIdentityProvider.DUMMY] == DummyProvider  # type: ignore[index]


def test_get_provider_error(monkeypatch: MonkeyPatch) -> None:
    # first remove the default provider from the registry
    monkeypatch.delitem(_PROVIDER_REGISTRY, IdentityProvider.MEMORY)

    # then get an error when we try to get an instance
    with pytest.raises(RuntimeError, match="Identity provider not implemented"):
        get_provider()


def test_get_provider() -> None:
    SETTINGS_STORE.reset()
    settings = DummySettings.get()
    settings.identity_provider = DummyIdentityProvider.DUMMY

    register_provider(DummyIdentityProvider.DUMMY, DummyProvider)  # type: ignore[arg-type]

    provider = get_provider()
    assert isinstance(provider, DummyProvider)
