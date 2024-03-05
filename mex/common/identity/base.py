from abc import abstractmethod

from mex.common.connector import BaseConnector
from mex.common.identity.models import Identity
from mex.common.types import AnyMergedIdentifier, MergedPrimarySourceIdentifier


class BaseProvider(BaseConnector):
    """Base class to define the interface of identity providers."""

    @abstractmethod
    def assign(
        self,
        had_primary_source: MergedPrimarySourceIdentifier,
        identifier_in_primary_source: str,
    ) -> Identity:  # pragma: no cover
        """Find an Identity in a database or assign a new one."""
        ...

    @abstractmethod
    def fetch(
        self,
        *,
        had_primary_source: MergedPrimarySourceIdentifier | None = None,
        identifier_in_primary_source: str | None = None,
        stable_target_id: AnyMergedIdentifier | None = None,
    ) -> list[Identity]:  # pragma: no cover
        """Find Identity instances matching the given filters."""
        ...
