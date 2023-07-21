import warnings

from mex.common.identity.base import BaseProvider
from mex.common.identity.models import Identity
from mex.common.identity.query import fetch_identity, upsert_identity
from mex.common.types import Identifier


class IdentityConnector(BaseProvider):
    """Connector class to handle read/write to the identity database."""

    @classmethod
    def get(cls) -> "IdentityConnector":
        """Create or retrieve an identity provider from the context."""
        return cls()

    def upsert(self, *args: Identifier | str) -> Identity:
        """Insert a new identity or update an existing one."""
        warnings.warn(
            "IdentityConnector.upsert is deprecated. Use upsert_identity instead.",
            DeprecationWarning,
        )
        return upsert_identity(*args)  # type: ignore

    def fetch(self, **kwargs: Identifier | str | None) -> Identity | None:
        """Find an Identity instance from the database if it can be found."""
        warnings.warn(
            "IdentityConnector.fetch is deprecated. Use fetch_identity instead.",
            DeprecationWarning,
        )
        return fetch_identity(**kwargs)  # type: ignore
