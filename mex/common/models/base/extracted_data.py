from typing import Annotated, TypeVar

from pydantic import Field

from mex.common.models.base.model import BaseModel
from mex.common.transform import camel_to_split
from mex.common.types import (
    ExtractedIdentifier,
    MergedIdentifier,
    MergedPrimarySourceIdentifier,
)

_MergedIdentifierT = TypeVar("_MergedIdentifierT", bound=MergedIdentifier)
_ExtractedIdentifierT = TypeVar("_ExtractedIdentifierT", bound=ExtractedIdentifier)

HadPrimarySource = Annotated[
    MergedPrimarySourceIdentifier,
    Field(
        json_schema_extra={"sameAs": ["http://www.w3.org/ns/prov#hadPrimarySource"]},
        frozen=True,
        description=(
            "A primary source for a topic refers to something produced by some "
            "agent with direct experience and knowledge about the topic, at the "
            "time of the topic's study, without benefit from hindsight. Because "
            "of the directness of primary sources, they 'speak for themselves' "
            "in ways that cannot be captured through the filter of secondary "
            "sources. As such, it is important for secondary sources to reference "
            "those primary sources from which they were derived, so that their "
            "reliability can be investigated. A primary source relation is a "
            "particular case of derivation of secondary materials from their "
            "primary sources. It is recognized that the determination of primary "
            "sources can be up to interpretation, and should be done according to "
            "conventions accepted within the application's domain ([PROV-O, "
            "2013-04-30 ](http://www.w3.org/TR/2013/REC-prov-o-20130430/))."
        ),
    ),
]
IdentifierInPrimarySource = Annotated[
    str,
    Field(
        examples=["123456", "item-501", "D7/x4/zz.final3"],
        min_length=1,
        max_length=1000,
        pattern=r"^[^\n\r]+$",
        frozen=True,
        description="The identifier of the item used in the primary source.",
    ),
]


class ExtractedData(
    BaseModel,
    extra="forbid",
    model_title_generator=lambda m: camel_to_split(m.__name__),
):
    """Base model for all extracted item classes.

    This class adds two important attributes for metadata provenance: `hadPrimarySource`
    and `identifierInPrimarySource`, which are used to uniquely identify an
    item in its original primary source. The attribute `stableTargetId` has to be set
    by each concrete subclass, like `ExtractedPerson`, because it needs to have the
    correct type, e.g. `MergedPersonIdentifier`.

    This class also adds a validator to automatically set identifiers for provenance.
    """

    # The stableTargetId of the primary source, that this item was
    # extracted from. This field is mandatory for all extracted items to
    # aid with data provenance. Extracted primary sources also have this
    # field and are all extracted from a static primary source for MEx.
    # The extracted primary source for MEx has its own merged item as a
    # primary source.
    hadPrimarySource: HadPrimarySource
    # This is the identifier the original item had in its source system.
    # It is only unique amongst items coming from the same system, because
    # identifier formats are likely to overlap between systems.
    # The value for `identifierInPrimarySource` is therefore only unique in
    # composition with `hadPrimarySource`. MEx uses this composite key to
    # assign a stable and globally unique `identifier` per extracted item.
    identifierInPrimarySource: IdentifierInPrimarySource

    def _get_identifier(
        self, identifier_type: type[_ExtractedIdentifierT]
    ) -> _ExtractedIdentifierT:
        """Consult the identity provider to get the `identifier` for this item.

        Args:
            identifier_type: ExtractedIdentifier-subclass to cast the identifier to

        Returns:
            Identifier of the correct type
        """
        # break import cycle, sigh
        from mex.common.identity import get_provider  # noqa: PLC0415

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
        # break import cycle, sigh
        from mex.common.identity import get_provider  # noqa: PLC0415

        return identifier_type(
            get_provider()
            .assign(self.hadPrimarySource, self.identifierInPrimarySource)
            .stableTargetId
        )
