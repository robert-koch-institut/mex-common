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
        return self.identifier

    @property
    def platform_id(self) -> PrimarySourceID:
        """Return hadPrimarySource."""
        return self.hadPrimarySource

    @property
    def original_id(self) -> str:
        """Return identifierInPrimarySource."""
        return self.identifierInPrimarySource

    @property
    def merged_id(self) -> Identifier:
        """Return stableTargetId."""
        return self.stableTargetId

    @property
    def entity_type(self) -> str:
        """Return entityType."""
        return self.entityType
