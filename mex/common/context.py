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


class SingleSingletonStore(Generic[_SingletonT]):
    """Thin wrapper for storing a single thread-local singleton.

    Stores only a single instance. Requested class must either be
    the same or a parent class of the stored class.
    """

    def __init__(self) -> None:
        """Create a new settings singleton store."""
        self._singleton: _SingletonT | None = None

    def load(self, cls: type[_SingletonT]) -> _SingletonT:
        """Retrieve the settings for the given class or create a new one."""
        if self._singleton is None:
            self._singleton = cls()
            return self._singleton
        if not issubclass(type(self._singleton), cls):
            msg = (
                f"requested class ({cls}) is not a parent class of loaded class "
                f"({type(self._singleton)}). "
                f"Did you initialize {cls} upon startup?"
            )
            raise RuntimeError(msg)  # noqa: TRY004
        return self._singleton

    def push(self, instance: _SingletonT) -> None:
        """Set or replace a singleton instance in the store."""
        self._singleton = instance

    def reset(self) -> None:
        """Remove singleton instance from the store."""
        self._singleton = None
