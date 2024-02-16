from typing import Generic, TypeVar

ContextResource = TypeVar("ContextResource")


class ContextStore(Generic[ContextResource]):
    """Drop-in replacement for `ContextVar`s to store global instances.

    Since we are not using asynchronous code yet, we simply want to store
    configuration state or connection pools in a controlled way without
    worrying about concurrent context management.
    """

    def __init__(self, name: str, default: ContextResource) -> None:
        """Create a new context store with an identifiable name and a default value."""
        self._resource = default
        self._name = name

    def __repr__(self) -> str:
        """Return a named representation of this context store."""
        return f'Context("{self._name}")'

    def get(self) -> ContextResource:
        """Retrieve the current value stored in this context."""
        return self._resource

    def set(self, resource: ContextResource) -> None:
        """Update the current value stored in this context."""
        self._resource = resource
