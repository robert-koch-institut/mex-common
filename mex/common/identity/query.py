from mex.common.exceptions import MExError
from mex.common.identity.dummy import DummyIdentityProvider
from mex.common.identity.models import Identity
from mex.common.identity.types import IdentityProvider
from mex.common.settings import BaseSettings
from mex.common.types import Identifier


def upsert_identity(
    had_primary_source: Identifier,
    identifier_in_primary_source: str,
    stable_target_id: Identifier,
    entity_type: str,
) -> Identity:
    """Insert a new identity or update an existing one."""
    settings = BaseSettings.get()
    if settings.identity_provider == IdentityProvider.DUMMY:
        provider = DummyIdentityProvider.get()
        return provider.upsert(
            had_primary_source,
            identifier_in_primary_source,
            stable_target_id,
            entity_type,
        )
    raise MExError(f"Cannot upsert identity to {settings.identity_provider}")


def fetch_identity(
    *,
    had_primary_source: Identifier | None = None,
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
