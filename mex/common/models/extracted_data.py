from typing import Any

from pydantic import Field, model_validator

from mex.common.models.base import MExModel
from mex.common.types import Identifier, PrimarySourceID

MEX_PRIMARY_SOURCE_STABLE_TARGET_ID = PrimarySourceID("00000000000000")
MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE = "mex"


class BaseExtractedData(MExModel):
    """Base model class definition for all extracted data instances."""

    hadPrimarySource: PrimarySourceID = Field(
        ..., examples=[Identifier.generate(seed=42)]
    )
    identifierInPrimarySource: str = Field(
        ..., examples=["123456", "item-501", "D7/x4/zz.final3"], min_length=1
    )

    @classmethod
    def get_entity_type(cls) -> str:
        """Get the schema-conform name of this model class."""
        return cls.__name__

    def __str__(self) -> str:
        """Format this extracted data instance as a string for logging."""
        return (
            f"{self.__class__.__name__}: "
            f"{self.identifierInPrimarySource} "
            f"{self.identifier} "
            f"{self.stableTargetId}"
        )


class ExtractedData(BaseExtractedData):
    """Base model class for extracted data instances that ensures identities."""

    @model_validator(mode="before")
    @classmethod
    def set_identifiers(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Ensure identifier and provenance attributes are set for this instance.

        A lookup is performed to determine whether this extracted data instance already
        has an `identifier` or `stableTargetId`.
        If not, new ones are generated and the association remembered.

        If the `identifier` field has been set manually, e.g. passed to the constructor,
        we check that it is already present in the identity provider and is assigned to
        the same extracted data instance: it must be the same combination of
        `identifier`, `hadPrimarySource` and `identifierInPrimarySource`.
        If the identity is not found or the `identifier` differs, an error is thrown.
        An exception is made for the MEx primary source which serves as the root node
        for all relations: it may the `stableTargetId` manually.

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
        from mex.common.identity.query import fetch_identity, upsert_identity

        # validate ID in primary source and primary source ID
        if identifier_in_primary_source := values.get("identifierInPrimarySource"):
            identifier_in_primary_source = str(identifier_in_primary_source)
        else:
            raise ValueError("Missing value for `identifierInPrimarySource`.")

        if had_primary_source := values.get("hadPrimarySource"):
            had_primary_source = PrimarySourceID(had_primary_source)
        else:
            raise ValueError("Missing value for `hadPrimarySource`.")

        identity = fetch_identity(
            had_primary_source=had_primary_source,
            identifier_in_primary_source=identifier_in_primary_source,
        )

        # validate extracted data ID
        if identifier := values.get("identifier"):
            if identity is None:
                raise ValueError("Identifier not found by identity provider.")
            if identity.identifier != str(identifier):
                raise ValueError("Identifier cannot be set manually to new value.")

        # validate stable target ID
        if stable_target_id := values.get("stableTargetId"):
            if (
                identity is None
                and stable_target_id != MEX_PRIMARY_SOURCE_STABLE_TARGET_ID
            ):
                raise ValueError("Stable target ID not found by identity provider.")
            stable_target_id = Identifier(stable_target_id)
        elif identity:
            stable_target_id = Identifier(identity.stableTargetId)
        else:
            stable_target_id = Identifier.generate()

        # update identity map
        identity = upsert_identity(
            had_primary_source,
            identifier_in_primary_source,
            stable_target_id,
            cls.get_entity_type(),
        )

        # update instance values
        values["identifier"] = Identifier(identity.identifier)
        values["stableTargetId"] = Identifier(identity.stableTargetId)
        return values
