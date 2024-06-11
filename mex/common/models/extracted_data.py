from typing import TYPE_CHECKING, Annotated, Generic, TypeVar, cast

from pydantic import Field, computed_field

from mex.common.models.entity import BaseEntity
from mex.common.types import (
    ExtractedPrimarySourceIdentifier,
    MergedPrimarySourceIdentifier,
)
from mex.common.types.identifier import ExtractedIdentifier, MergedIdentifier

MEX_PRIMARY_SOURCE_IDENTIFIER = ExtractedPrimarySourceIdentifier("00000000000001")
MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE = "mex"
MEX_PRIMARY_SOURCE_STABLE_TARGET_ID = MergedPrimarySourceIdentifier("00000000000000")

ExtractedIdentifierT = TypeVar("ExtractedIdentifierT", bound=ExtractedIdentifier)
MergedIdentifierT = TypeVar("MergedIdentifierT", bound=MergedIdentifier)


class ExtractedData(Generic[ExtractedIdentifierT, MergedIdentifierT], BaseEntity):
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

    if TYPE_CHECKING:  # pragma: no cover
        # avoiding mypy issues here by typing the computed fields as property stubs
        # https://docs.pydantic.dev/latest/api/fields/#pydantic.fields.computed_field

        @property
        def identifier(self) -> ExtractedIdentifierT:  # noqa: D102
            ...

        @property
        def stableTargetId(self) -> MergedIdentifierT:  # noqa: D102, N802
            ...

    else:

        @computed_field
        def identifier(self) -> ExtractedIdentifierT:
            """Return the computed identifier for this extracted data item."""
            from mex.common.identity import assign_identity  # break import cycle, sigh

            return cast(ExtractedIdentifierT, assign_identity(self).identifier)

        @computed_field
        def stableTargetId(self) -> MergedIdentifierT:  # noqa: N802
            """Return the computed stableTargetId for this extracted data item."""
            from mex.common.identity import assign_identity  # break import cycle, sigh

            return cast(MergedIdentifierT, assign_identity(self).stableTargetId)
