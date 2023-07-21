from enum import Enum


class IdentityProvider(Enum):
    """Choice of available identity providers."""

    BACKEND = "backend"
    DUMMY = "dummy"
