from collections.abc import Generator

import pytest

from mex.common.identity.memory import MemoryIdentityProvider
from mex.common.identity.registry import _PROVIDER_REGISTRY, register_provider
from mex.common.types import IdentityProvider


@pytest.fixture(autouse=True)
def isolate_provider_registry() -> Generator[None, None, None]:
    """Restore the provider registry after each identity test."""
    yield
    _PROVIDER_REGISTRY.clear()
    register_provider(IdentityProvider.MEMORY, MemoryIdentityProvider)
