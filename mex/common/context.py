from collections.abc import Iterator
from typing import Generic, TypeVar

_T = TypeVar("_T")


class SingletonStore(Generic[_T]):
    """Thin wrapper for storing thread-local singletons."""

    def __init__(self) -> None:
        """Create a new singleton store with the given type."""
        self._instances_by_class: dict[type[_T], _T] = {}

    def __iter__(self) -> Iterator[_T]:
        """Return an iterator over all singletons in the store."""
        return iter(self._instances_by_class.values())

    def load(self, cls: type[_T]) -> _T:
        """Retrieve a singleton for the given class or create a new one."""
        if cls not in self._instances_by_class:
            self.push(cls())
        return self._instances_by_class[cls]

    def push(self, instance: _T) -> None:
        """Set or replace a singleton instance in the store."""
        self._instances_by_class[type(instance)] = instance

    def pop(self, cls: type[_T]) -> _T:
        """Remove a singleton for the given class for the store and return it."""
        return self._instances_by_class.pop(cls)

    def reset(self) -> None:
        """Remove all singleton instances from the store."""
        self._instances_by_class.clear()
