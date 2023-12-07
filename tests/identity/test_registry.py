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
from mex.common.settings import BaseSettings
from mex.common.types import IdentityProvider


class DummyIdentityProvider(Enum):
    DUMMY = "dummy"


class DummyProvider(BaseProvider):
    def __init__(self) -> None:
        pass

    def assign(self, *_: str) -> Identity:
        raise RuntimeError()

    def fetch(self, **_: str | None) -> list[Identity]:
        raise RuntimeError()

    def close(self) -> None:
        pass


class DummySettings(BaseSettings):
    identity_provider: IdentityProvider | DummyIdentityProvider = (
        IdentityProvider.MEMORY
    )


def test_register_provider_error() -> None:
    with pytest.raises(RuntimeError, match="Already registered identity provider"):
        register_provider(IdentityProvider.MEMORY, MemoryIdentityProvider)


def test_register_provider() -> None:
    register_provider(DummyIdentityProvider.DUMMY, DummyProvider)

    assert _PROVIDER_REGISTRY[DummyIdentityProvider.DUMMY] == DummyProvider


def test_get_provider_error(monkeypatch: MonkeyPatch) -> None:
    # first remove the default provider from the registry
    monkeypatch.delitem(_PROVIDER_REGISTRY, IdentityProvider.MEMORY)

    # then get an error when we try to get an instance
    with pytest.raises(RuntimeError, match="Identity provider not implemented"):
        get_provider()


def test_get_provider() -> None:
    settings = DummySettings.get()
    settings.identity_provider = DummyIdentityProvider.DUMMY

    register_provider(DummyIdentityProvider.DUMMY, DummyProvider)

    provider = get_provider()
    assert isinstance(provider, DummyProvider)
