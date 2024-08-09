from typing import Annotated, TypeVar

from pydantic import Field

from mex.common.models.base.entity import BaseEntity
from mex.common.types import (
    ExtractedIdentifier,
    MergedIdentifier,
    MergedPrimarySourceIdentifier,
)

_MergedIdentifierT = TypeVar("_MergedIdentifierT", bound=MergedIdentifier)
_ExtractedIdentifierT = TypeVar("_ExtractedIdentifierT", bound=ExtractedIdentifier)


class ExtractedData(BaseEntity):
    """Base model for all extracted data classes.

    This class adds two important attributes for metadata provenance: `hadPrimarySource`
    and `identifierInPrimarySource`, which are used to uniquely identify an
    item in its original primary source. The attribute `stableTargetId` has to be set
    by each concrete subclass, like `ExtractedPerson`, because it needs to have the
    correct type, e.g. `MergedPersonIdentifier`.

    This class also adds a validator to automatically set identifiers for provenance.
    See below, for a full description.
    """

    hadPrimarySource: Annotated[
        MergedPrimarySourceIdentifier,
        Field(
            description=(
                "The stableTargetId of the primary source, that this item was "
                "extracted from. This field is mandatory for all extracted items to "
                "aid with data provenance. Extracted primary sources also have this "
                "field and are all extracted from a static primary source for MEx. "
                "The extracted primary source for MEx has its own merged item as a "
                "primary source."
            ),
            frozen=True,
        ),
    ]
    identifierInPrimarySource: Annotated[
        str,
        Field(
            description=(
                "This is the identifier the original item had in its source system. "
                "It is only unique amongst items coming from the same system, because "
                "identifier formats are likely to overlap between systems. "
                "The value for `identifierInPrimarySource` is therefore only unique in "
                "composition with `hadPrimarySource`. MEx uses this composite key to "
                "assign a stable and globally unique `identifier` per extracted item."
            ),
            examples=["123456", "item-501", "D7/x4/zz.final3"],
            min_length=1,
            frozen=True,
        ),
    ]

    def _get_identifier(
        self, identifier_type: type[_ExtractedIdentifierT]
    ) -> _ExtractedIdentifierT:
        """Consult the identity provider to get the `identifier` for this item.

        Args:
            identifier_type: ExtractedIdentifier-subclass to cast the identifier to

        Returns:
            Identifier of the correct type
        """
        from mex.common.identity import get_provider  # break import cycle, sigh

        return identifier_type(
            get_provider()
            .assign(self.hadPrimarySource, self.identifierInPrimarySource)
            .identifier
        )

    def _get_stable_target_id(
        self, identifier_type: type[_MergedIdentifierT]
    ) -> _MergedIdentifierT:
        """Consult the identity provider to get the `stableTargetId` for this item.

        Args:
            identifier_type: MergedIdentifier-subclass to cast the identifier to

        Returns:
            StableTargetId of the correct type
        """
        from mex.common.identity import get_provider  # break import cycle, sigh

        return identifier_type(
            get_provider()
            .assign(self.hadPrimarySource, self.identifierInPrimarySource)
            .stableTargetId
        )
