class MExError(Exception):
    """Base class for generic exceptions."""

    def __str__(self) -> str:
        """Format this exception as a string for logging."""
        return (
            f"{self.__class__.__name__}: "
            f"{(', '.join((str(arg) for arg in self.args)))} "
        )


class EmptySearchResultError(MExError):
    """Empty search result."""


class FoundMoreThanOneError(MExError):
    """Found more than one."""
