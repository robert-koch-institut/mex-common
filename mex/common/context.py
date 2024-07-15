from collections.abc import Iterator
from typing import Generic, TypeVar

_SingletonT = TypeVar("_SingletonT")


class SingletonStore(Generic[_SingletonT]):
    """Thin wrapper for storing thread-local singletons."""

    def __init__(self) -> None:
        """Create a new singleton store with the given type."""
        self._instances_by_class: dict[type[_SingletonT], _SingletonT] = {}

    def __iter__(self) -> Iterator[_SingletonT]:
        """Return an iterator over all singletons in the store."""
        return iter(self._instances_by_class.values())

    def load(self, cls: type[_SingletonT]) -> _SingletonT:
        """Retrieve a singleton for the given class or create a new one."""
        if cls not in self._instances_by_class:
            self.push(cls())
        return self._instances_by_class[cls]

    def push(self, instance: _SingletonT) -> None:
        """Set or replace a singleton instance in the store."""
        self._instances_by_class[type(instance)] = instance

    def pop(self, cls: type[_SingletonT]) -> _SingletonT:
        """Remove a singleton for the given class for the store and return it."""
        return self._instances_by_class.pop(cls)

    def reset(self) -> None:
        """Remove all singleton instances from the store."""
        self._instances_by_class.clear()
