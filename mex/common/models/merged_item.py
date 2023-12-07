from mex.common.models.base import MExModel


class MergedItem(MExModel):
    """Base model class definition for all merged items."""

    def __str__(self) -> str:
        """Format this merged item instance as a string for logging."""
        return f"{self.__class__.__name__}: {self.identifier}"
