from typing import Generic, TypeVar

ContextResource = TypeVar("ContextResource")


class ContextStore(Generic[ContextResource]):
    """Thin wrapper for storing thread-local globals."""

    def __init__(self, default: ContextResource) -> None:
        """Create a new context store with a default value."""
        self._resource = default

    def get(self) -> ContextResource:
        """Retrieve the current value stored in this context."""
        return self._resource

    def set(self, resource: ContextResource) -> None:
        """Update the current value stored in this context."""
        self._resource = resource
