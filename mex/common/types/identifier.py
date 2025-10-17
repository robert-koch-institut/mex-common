import string
from typing import Any, Self
from uuid import UUID, uuid4

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, json_schema
from pydantic_core import core_schema

_ALPHABET = string.ascii_letters + string.digits
IDENTIFIER_PATTERN = r"^[a-zA-Z0-9]{14,22}$"


class Identifier(str):
    """Common identifier class based on UUID version 4."""

    __slots__ = ()

    @classmethod
    def generate(cls, seed: int | None = None) -> Self:
        """Generate a new identifier from a seed or random UUID version 4.

        Creates a short alphanumerical identifier using UUID version 4 as the
        source. If a seed is provided, the UUID will be deterministic; otherwise
        a random UUID is generated.

        Args:
            seed: Optional integer seed for deterministic identifier generation.
                  If None, generates a random identifier.

        Returns:
            New identifier instance with the generated value.
        """
        # Inspired by https://pypi.org/project/shortuuid
        output = ""
        alpha_len = len(_ALPHABET)
        if seed is None:
            number = uuid4().int
        else:
            number = UUID(int=seed, version=4).int
        while number:
            number, digit = divmod(number, alpha_len)
            output += _ALPHABET[digit]
        return cls(output[::-1])

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """Modify the core schema to add the ID regex."""
        return core_schema.chain_schema(
            [
                core_schema.str_schema(pattern=IDENTIFIER_PATTERN),
                core_schema.no_info_plain_validator_function(cls),
            ],
            serialization=core_schema.to_string_ser_schema(when_used="unless-none"),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema_: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> json_schema.JsonSchemaValue:
        """Modify the json schema to add the class name as title."""
        json_schema_ = handler(core_schema_)
        json_schema_ = handler.resolve_ref_schema(json_schema_)
        json_schema_["title"] = cls.__name__
        json_schema_["pattern"] = IDENTIFIER_PATTERN
        return json_schema_

    def __repr__(self) -> str:
        """Overwrite the default representation."""
        return f'{self.__class__.__name__}("{self}")'


# We have technically-identical subclasses of identifier types (one per entity-type).
# This allows us to annotate which entity-types are allowed on reference fields.
# For example `contact: MergedPersonIdentifier | MergedOrganizationIdentifier` tells us
# that a contact for an item has to be either a merged person or merged organization.
# We cannot validate this using pydantic, because all identifiers have the same
# format. But it helps for documentation purposes, allows us to generate a more
# precise JSON schema definitions and to derive database queries from the models.


class ExtractedIdentifier(Identifier):
    """Base class for all extracted identifiers."""


class ExtractedAccessPlatformIdentifier(ExtractedIdentifier):
    """Identifier for extracted access platforms."""


class ExtractedActivityIdentifier(ExtractedIdentifier):
    """Identifier for extracted activities."""


class ExtractedBibliographicResourceIdentifier(ExtractedIdentifier):
    """Identifier for extracted bibliographic resources."""


class ExtractedConsentIdentifier(ExtractedIdentifier):
    """Identifier for extracted consents."""


class ExtractedContactPointIdentifier(ExtractedIdentifier):
    """Identifier for extracted contact points."""


class ExtractedDistributionIdentifier(ExtractedIdentifier):
    """Identifier for extracted distributions."""


class ExtractedOrganizationIdentifier(ExtractedIdentifier):
    """Identifier for extracted organizations."""


class ExtractedOrganizationalUnitIdentifier(ExtractedIdentifier):
    """Identifier for extracted organizational units."""


class ExtractedPersonIdentifier(ExtractedIdentifier):
    """Identifier for extracted persons."""


class ExtractedPrimarySourceIdentifier(ExtractedIdentifier):
    """Identifier for extracted primary sources."""


class ExtractedResourceIdentifier(ExtractedIdentifier):
    """Identifier for extracted resources."""


class ExtractedVariableIdentifier(ExtractedIdentifier):
    """Identifier for extracted variables."""


class ExtractedVariableGroupIdentifier(ExtractedIdentifier):
    """Identifier for extracted variable groups."""


class MergedIdentifier(Identifier):
    """Base class for all merged identifiers."""


class MergedAccessPlatformIdentifier(MergedIdentifier):
    """Identifier for merged access platforms."""


class MergedActivityIdentifier(MergedIdentifier):
    """Identifier for merged activities."""


class MergedBibliographicResourceIdentifier(MergedIdentifier):
    """Identifier for merged bibliographic resources."""


class MergedConsentIdentifier(MergedIdentifier):
    """Identifier for merged consents."""


class MergedContactPointIdentifier(MergedIdentifier):
    """Identifier for merged contact points."""


class MergedDistributionIdentifier(MergedIdentifier):
    """Identifier for merged distributions."""


class MergedOrganizationIdentifier(MergedIdentifier):
    """Identifier for merged organizations."""


class MergedOrganizationalUnitIdentifier(MergedIdentifier):
    """Identifier for merged organizational units."""


class MergedPersonIdentifier(MergedIdentifier):
    """Identifier for merged persons."""


class MergedPrimarySourceIdentifier(MergedIdentifier):
    """Identifier for merged primary sources."""


class MergedResourceIdentifier(MergedIdentifier):
    """Identifier for merged resources."""


class MergedVariableIdentifier(MergedIdentifier):
    """Identifier for merged variables."""


class MergedVariableGroupIdentifier(MergedIdentifier):
    """Identifier for merged variable groups."""
