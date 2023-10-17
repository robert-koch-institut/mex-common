from abc import ABCMeta, abstractmethod
from enum import Enum

from mex.common.identity.models import Identity
from mex.common.types import Identifier, PrimarySourceID


class IdentityProvider(Enum):
    """Choice of available identity providers."""

    BACKEND = "backend"
    DUMMY = "dummy"


class BaseProvider(metaclass=ABCMeta):
    """Base class to define the interface of identity providers."""

    @abstractmethod
    def assign(
        self,
        had_primary_source: PrimarySourceID,
        identifier_in_primary_source: str,
    ) -> Identity:  # pragma: no cover
        """Find an Identity or assign a new one."""
        ...

    @abstractmethod
    def fetch(
        self,
        *,
        had_primary_source: Identifier | None = None,
        identifier_in_primary_source: str | None = None,
        stable_target_id: Identifier | None = None,
    ) -> Identity | None:  # pragma: no cover
        """Find an Identity instance from the database if it can be found."""
        ...
