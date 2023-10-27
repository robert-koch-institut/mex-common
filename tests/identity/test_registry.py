from enum import Enum

import pytest
from pytest import MonkeyPatch

from mex.common.identity.base import BaseProvider
from mex.common.identity.dummy import DummyIdentityProvider
from mex.common.identity.models import Identity
from mex.common.identity.registry import (
    _PROVIDER_REGISTRY,
    get_provider,
    register_provider,
)
from mex.common.identity.types import IdentityProvider
from mex.common.settings import BaseSettings


class ExampleIdentityProvider(Enum):
    EXAMPLE = "example"


class ExampleProvider(BaseProvider):
    def __init__(self) -> None:
        pass

    def assign(self, *_: str) -> Identity:
        raise RuntimeError()

    def fetch(self, **_: str | None) -> list[Identity]:
        raise RuntimeError()

    def close(self) -> None:
        pass


class ExampleSettings(BaseSettings):
    identity_provider: IdentityProvider | ExampleIdentityProvider = (
        IdentityProvider.DUMMY
    )


def test_register_provider_error() -> None:
    with pytest.raises(RuntimeError, match="Already registered identity provider"):
        register_provider(IdentityProvider.DUMMY, DummyIdentityProvider)


def test_register_provider() -> None:
    register_provider(ExampleIdentityProvider.EXAMPLE, ExampleProvider)

    assert _PROVIDER_REGISTRY[ExampleIdentityProvider.EXAMPLE] == ExampleProvider


def test_get_provider_error(monkeypatch: MonkeyPatch) -> None:
    # first remove the dummy provider from the registry
    monkeypatch.delitem(_PROVIDER_REGISTRY, IdentityProvider.DUMMY)

    # then get an error when we try to get an instance
    with pytest.raises(RuntimeError, match="Identity provider not implemented"):
        get_provider()


def test_get_provider() -> None:
    settings = ExampleSettings.get()
    settings.identity_provider = ExampleIdentityProvider.EXAMPLE

    register_provider(ExampleIdentityProvider.EXAMPLE, ExampleProvider)

    provider = get_provider()
    assert isinstance(provider, ExampleProvider)
