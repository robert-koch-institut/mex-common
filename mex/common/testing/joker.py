class Joker:  # noqa: PLW1641
    """Testing utility that pretends to be equal to anything.

    Useful for tests that assert partially predictable dictionaries.

    Example:
        assert value == {"predictable": 42, "timestamp": Joker()}
    """

    _repr_cache: str | None = None

    def __eq__(self, obj: object) -> bool:
        """Pretend to be equal to any other object."""
        self._repr_cache = repr(obj)
        return True

    def __repr__(self) -> str:
        """Pretend to have the same representation as the last compared-to object."""
        # This hack allows pytest to print dict diffs without outlining jokers as diffs.
        if self._repr_cache:
            return self._repr_cache
        return super().__repr__()
