import warnings

from mex.common.models import BaseModel
from mex.common.types import Identifier, PrimarySourceID


class Identity(BaseModel):
    """Model for identifier lookup."""

    identifier: Identifier
    hadPrimarySource: PrimarySourceID
    identifierInPrimarySource: str
    stableTargetId: Identifier
    entityType: str

    @property
    def fragment_id(self) -> Identifier:
        """Return identifier."""
        warnings.warn(
            "fragment_id is deprecated. Use identifier instead.", DeprecationWarning
        )
        return self.identifier

    @property
    def platform_id(self) -> PrimarySourceID:
        """Return hadPrimarySource."""
        warnings.warn(
            "platform_id is deprecated. Use hadPrimarySource instead.",
            DeprecationWarning,
        )
        return self.hadPrimarySource

    @property
    def original_id(self) -> str:
        """Return identifierInPrimarySource."""
        warnings.warn(
            "original_id is deprecated. Use identifierInPrimarySource instead.",
            DeprecationWarning,
        )
        return self.identifierInPrimarySource

    @property
    def merged_id(self) -> Identifier:
        """Return stableTargetId."""
        warnings.warn(
            "merged_id is deprecated. Use stableTargetId instead.", DeprecationWarning
        )
        return self.stableTargetId

    @property
    def entity_type(self) -> str:
        """Return entityType."""
        warnings.warn(
            "entity_type is deprecated. Use entityType instead.",
            DeprecationWarning,
        )
        return self.entityType
