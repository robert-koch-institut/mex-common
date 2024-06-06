from functools import cached_property
from typing import Annotated, Generic, TypeVar, cast

from pydantic import Field, computed_field

from mex.common.types import (
    ExtractedPrimarySourceIdentifier,
    MergedPrimarySourceIdentifier,
)
from mex.common.types.identifier import Identifier, MergedContactPointIdentifier

MEX_PRIMARY_SOURCE_IDENTIFIER = ExtractedPrimarySourceIdentifier("00000000000001")
MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE = "mex"
MEX_PRIMARY_SOURCE_STABLE_TARGET_ID = MergedPrimarySourceIdentifier("00000000000000")

IdentifierT = TypeVar("IdentifierT", bound=Identifier)
MergedIdentifierT = TypeVar("MergedIdentifierT", bound=Identifier)


class ExtractedData(Generic[IdentifierT, MergedIdentifierT]):
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

    @computed_field
    @cached_property
    def identifier(self) -> IdentifierT:  # type: ignore[override]
        # break import cycle, sigh
        from mex.common.identity import get_provider

        provider = get_provider()
        identity = provider.assign(
            self.hadPrimarySource, self.identifierInPrimarySource
        )
        return cast(IdentifierT, identity.identifier)

    @computed_field
    @cached_property
    def stableTargetId(self) -> MergedContactPointIdentifier:
        # break import cycle, sigh
        from mex.common.identity import get_provider

        provider = get_provider()
        identity = provider.assign(
            self.hadPrimarySource, self.identifierInPrimarySource
        )
        return cast(MergedContactPointIdentifier, identity.stableTargetId)
