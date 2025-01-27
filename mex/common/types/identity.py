from enum import Enum


class IdentityProvider(Enum):
    """Choice of available identity providers."""

    BACKEND = "backend"
    GRAPH = "graph"
    MEMORY = "memory"
