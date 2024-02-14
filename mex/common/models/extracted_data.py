from typing import TYPE_CHECKING, Annotated, Any

from pydantic import Field, model_validator, validate_call

from mex.common.models.base import MExModel
from mex.common.types import Identifier, PrimarySourceID

MEX_PRIMARY_SOURCE_IDENTIFIER = Identifier("00000000000000")
MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE = "mex"
MEX_PRIMARY_SOURCE_STABLE_TARGET_ID = PrimarySourceID("00000000000000")


class ExtractedData(MExModel):
    """Base model for all extracted data classes.

    This class adds two important attributes for metadata provenance: `hadPrimarySource`
    and `identifierInPrimarySource`, which are used to uniquely identify an
    item in its original primary source. The attribute `stableTargetId` has to be set
    by each concrete subclass, like `ExtractedPerson`, because it needs to have the
    correct type, e.g. `PersonID`.

    This class also adds a validator to automatically set identifiers for provenance.
    See below, for a full description.
    """

    if TYPE_CHECKING:
        # Sometimes multiple primary sources describe the same activity, resource, etc.
        # and a complete metadata item can only be created by merging these fragments.
        # The `stableTargetID` is part of all models in `mex.common.models` to allow
        # MEx to identify which extracted items describe the same thing and should be
        # merged to create a complete metadata item.
        # The name might be a bit misleading (also due to historical reasons), but the
        # "stability" is only guaranteed for one "real world" or "digital world" thing
        # having the same ID in MEx over time. But not as a guarantee, that the same
        # metadata sources contribute to the complete metadata item.
        # Because we anticipate that items have to be merged, the `stableTargetID` is
        # also used as the foreign key for all fields containing references.
        stableTargetId: Any

    hadPrimarySource: Annotated[
        PrimarySourceID,
        Field(
            description=(
                "The stableTargetID of the primary source, that this item was "
                "extracted from. This field is mandatory for all extracted items to "
                "aid with data provenance. Extracted primary sources also have this "
                "field and are all extracted from a static primary source for MEx. "
                "The primary source for MEx has itself as a primary source, which "
                "is meant to be the only loop in the graph formed by MEx metadata."
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
                "composition with `hadPrimarySource`. MEx uses this composite key "
                "to assign a stable and globally unique `identifier` to each item."
            ),
            examples=["123456", "item-501", "D7/x4/zz.final3"],
            min_length=1,
            frozen=True,
        ),
    ]

    # TODO make stable_target_id and identifier computed fields (MX-1435)
    @model_validator(mode="before")
    @classmethod
    @validate_call
    def set_identifiers(cls, values: dict[str, Any]) -> dict[str, Any]:  # noqa: C901
        """Ensure identifier and provenance attributes are set for this instance.

        All extracted data classes have four important identifiers that are defined
        by `MExModel` and `BaseExtractedData`:

        - identifierInPrimarySource
        - hadPrimarySource
        - identifier
        - stableTargetId

        Every time we create a new instance of an extracted item, we automatically
        validate that these identifiers are set correctly.

        We check that `identifierInPrimarySource` and `hadPrimarySource` are provided,
        because otherwise we cannot reliably determine the origin of this item.
        These two identifiers are the only two that need to be set during extraction.

        Next we query the configured `IdentityProvider` to determine whether this item
        already has an `identifier` and `stableTargetId`. If not, we let the identity
        provider generate new identifiers.

        If an `identifier` has been passed to the constructor, we check that it matches
        with what we got from the identity provider, because we don't allow any system
        to change the association from `identifierInPrimarySource` and
        `hadPrimarySource` to the `identifier`.
        A use case for passing a matching `identifier` to the constructor would be
        parsing an already extracted item from an NDJSON file or an API endpoint.

        If a `stableTargetId` has been passed to the constructor, we use that as the
        new value, because changes to the stable target ID are generally allowed.
        A use case for changing the `stableTargetId` will be the matching of
        multiple extracted items (see `MExModel.stableTargetId` for details).

        Args:
            values: Raw values to validate

        Raises:
            ValueError: If `identifier` was supplied but does not match the id provider
            ValueError: If `identifierInPrimarySource` was missing
            ValueError: If `hadPrimarySource` was missing

        Returns:
            Values with identifier and provenance attributes
        """
        # break import cycle, sigh
        from mex.common.identity import get_provider

        # validate ID in primary source and primary source ID
        if identifier_in_primary_source := values.get("identifierInPrimarySource"):
            if isinstance(identifier_in_primary_source, list):
                if len(identifier_in_primary_source) == 1:
                    identifier_in_primary_source = str(identifier_in_primary_source[0])
                else:
                    raise ValueError(
                        f"Expected one value for identifierInPrimarySource, "
                        f"got {len(identifier_in_primary_source)}"
                    )
            else:
                identifier_in_primary_source = str(identifier_in_primary_source)
        else:
            raise ValueError("Missing value for `identifierInPrimarySource`.")

        if had_primary_source := values.get("hadPrimarySource"):
            if isinstance(had_primary_source, list):
                if len(had_primary_source) == 1:
                    had_primary_source = PrimarySourceID(had_primary_source[0])
                else:
                    raise ValueError(
                        f"Expected one value for hadPrimarySource, "
                        f"got {len(had_primary_source)}"
                    )
            else:
                had_primary_source = PrimarySourceID(had_primary_source)
        else:
            raise ValueError("Missing value for `hadPrimarySource`.")

        provider = get_provider()
        identity = provider.assign(had_primary_source, identifier_in_primary_source)

        # In case an identity was already found and it differs from the identifier
        # provided to the constructor, we raise an error because it should not be
        # allowed to change the identifier of an existing item.
        if identifier := values.get("identifier"):
            if isinstance(identifier, list):
                if len(identifier) == 1:
                    identifier = identifier[0]
                else:
                    raise ValueError(
                        f"Expected one value for Identifier, got {len(identifier)}"
                    )
            if identity.identifier != str(identifier):
                raise ValueError("Identifier cannot be set manually to new value.")

        # In case an identity was found, we allow assigning a new stable target ID
        # for the purpose of merging two items, except for the MEx
        # primary source itself.
        if stable_target_id := values.get("stableTargetId"):
            if isinstance(stable_target_id, list):
                if len(stable_target_id) == 1:
                    stable_target_id = stable_target_id[0]
                else:
                    raise ValueError(
                        f"Expected one value for stableTargetId, "
                        f"got {len(stable_target_id)}"
                    )
            if (
                identity.stableTargetId != str(stable_target_id)
                and stable_target_id != MEX_PRIMARY_SOURCE_STABLE_TARGET_ID
            ):
                raise ValueError(
                    "Cannot change `stableTargetId` of MEx primary source."
                )

        # update instance values
        values["identifier"] = identity.identifier
        values["stableTargetId"] = identity.stableTargetId
        return values
