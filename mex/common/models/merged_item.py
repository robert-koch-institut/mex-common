from mex.common.models.base import MExModel


class MergedItem(MExModel):
    """Base model class definition for all merged items."""

    @classmethod
    def get_entity_type(cls) -> str:
        """Get the entity-type for this model class."""
        return cls.__name__

    def __str__(self) -> str:
        """Format this merged item instance as a string for logging."""
        return f"{self.__class__.__name__}: {self.identifier} "
