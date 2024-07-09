from typing import Annotated, Any, TypeVar

from pydantic import Field

from mex.common.models.entity import BaseEntity
from mex.common.types import (
    ExtractedIdentifier,
    ExtractedPrimarySourceIdentifier,
    MergedIdentifier,
    MergedPrimarySourceIdentifier,
)

MEX_PRIMARY_SOURCE_IDENTIFIER = ExtractedPrimarySourceIdentifier("00000000000001")
MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE = "mex"
MEX_PRIMARY_SOURCE_STABLE_TARGET_ID = MergedPrimarySourceIdentifier("00000000000000")

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
        self, type_: type[_ExtractedIdentifierT]
    ) -> _ExtractedIdentifierT:
        # break import cycle, sigh
        from mex.common.identity import get_provider

        provider = get_provider()
        return type_(
            provider.assign(
                self.hadPrimarySource, self.identifierInPrimarySource
            ).identifier
        )

    def _set_identifier(self, obj: Any) -> None:
        if ExtractedIdentifier(obj) != self._get_identifier(ExtractedIdentifier):
            raise ValueError("identifier cannot be changed")

    # Sometimes multiple primary sources describe the same activity, resource, etc.
    # and a complete metadata item can only be created by merging these fragments.
    # The `stableTargetId` is part of all extracted models to allow MEx to identify
    # which items describe the same thing and should be merged to create a complete
    # metadata item. The name `stableTargetId` might be a bit misleading, because
    # the "stability" is only guaranteed for one "real world" or "digital world"
    # thing having the same ID in MEx over time. But it is not a guarantee, that the
    # same metadata sources contribute to the complete metadata item. The naming has
    # its historical reasons, but we plan to change it in the near future.
    # Because we anticipate that items have to be merged, the `stableTargetId` is
    # also used as the foreign key for all fields containing references.

    def _get_stable_target_id(
        self, type_: type[_MergedIdentifierT]
    ) -> _MergedIdentifierT:
        from mex.common.identity import get_provider

        provider = get_provider()
        return type_(
            provider.assign(
                self.hadPrimarySource, self.identifierInPrimarySource
            ).stableTargetId
        )

    def _set_stable_target_id(self, obj: Any) -> None:
        if MergedIdentifier(obj) != self._get_stable_target_id(MergedIdentifier):
            raise ValueError("stableTargetId cannot be changed")
