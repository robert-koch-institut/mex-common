from mex.common.exceptions import MExError
from mex.common.identity.dummy import DummyIdentityProvider
from mex.common.identity.models import Identity
from mex.common.identity.types import IdentityProvider
from mex.common.settings import BaseSettings
from mex.common.types import Identifier, PrimarySourceID


def assign_identity(
    had_primary_source: PrimarySourceID,
    identifier_in_primary_source: str,
) -> Identity:
    """Find an Identity or assign a new one."""
    settings = BaseSettings.get()
    if settings.identity_provider == IdentityProvider.DUMMY:
        provider = DummyIdentityProvider.get()
        return provider.assign(had_primary_source, identifier_in_primary_source)
    raise MExError(f"Cannot assign identity to {settings.identity_provider}")


def fetch_identity(
    *,
    had_primary_source: PrimarySourceID | None = None,
    identifier_in_primary_source: str | None = None,
    stable_target_id: Identifier | None = None,
) -> Identity | None:
    """Find an Identity instance from the database if it can be found."""
    settings = BaseSettings.get()
    if settings.identity_provider == IdentityProvider.DUMMY:
        provider = DummyIdentityProvider.get()
        return provider.fetch(
            had_primary_source=had_primary_source,
            identifier_in_primary_source=identifier_in_primary_source,
            stable_target_id=stable_target_id,
        )
    raise MExError(f"Cannot fetch identity from {settings.identity_provider}")
