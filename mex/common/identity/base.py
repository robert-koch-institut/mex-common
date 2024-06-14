from abc import abstractmethod
from typing import TypeVar

from mex.common.connector import BaseConnector
from mex.common.identity.models import Identity
from mex.common.types import (
    AnyExtractedIdentifier,
    AnyMergedIdentifier,
    MergedIdentifier,
    MergedPrimarySourceIdentifier,
)

MergedIdentifierT = TypeVar("MergedIdentifierT", bound=MergedIdentifier)


class BaseProvider(BaseConnector):
    """Base class to define the interface of identity providers."""

    @abstractmethod
    def assign(
        self,
        had_primary_source: MergedPrimarySourceIdentifier,
        identifier_in_primary_source: str,
    ) -> Identity[AnyExtractedIdentifier, AnyMergedIdentifier]:  # pragma: no cover
        """Find an Identity in a database or assign a new one."""
        ...

    @abstractmethod
    def fetch(
        self,
        *,
        had_primary_source: MergedPrimarySourceIdentifier | None = None,
        identifier_in_primary_source: str | None = None,
        stable_target_id: MergedIdentifierT | None = None,
    ) -> list[Identity[AnyExtractedIdentifier, MergedIdentifierT]]:  # pragma: no cover
        """Find Identity instances matching the given filters."""
        ...
