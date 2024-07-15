import re
import string
from typing import Any, Self
from uuid import UUID, uuid4

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema

ALPHABET = string.ascii_letters + string.digits
MEX_ID_PATTERN = r"^[a-zA-Z0-9]{14,22}$"
UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"


class Identifier(str):
    """Common identifier class based on UUID version 4."""

    @classmethod
    def generate(cls, seed: int | None = None) -> Self:
        """Generate a new identifier from a seed or random UUID version 4."""
        # Inspired by https://pypi.org/project/shortuuid
        output = ""
        alpha_len = len(ALPHABET)
        if seed is None:
            number = uuid4().int
        else:
            number = UUID(int=seed, version=4).int
        while number:
            number, digit = divmod(number, alpha_len)
            output += ALPHABET[digit]
        return cls(output[::-1])

    @classmethod
    def validate(cls, value: Any) -> Self:
        """Validate a string, UUID or Identifier."""
        if isinstance(value, str | UUID | Identifier):
            value = str(value)
            if re.match(MEX_ID_PATTERN, value):
                return cls(value)
            if re.match(UUID_PATTERN, value):
                return cls.generate(seed=UUID(value).int)
            raise ValueError(f"Invalid identifier format: {value}")
        raise ValueError(f"Cannot parse {type(value)} as {cls.__name__}")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Modify the schema to add the ID regex."""
        identifier_schema = {
            "type": "str",
            "pattern": MEX_ID_PATTERN,
        }
        return core_schema.no_info_before_validator_function(
            cls.validate,
            identifier_schema,
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema_: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Modify the schema to add the class name as title."""
        json_schema = handler(core_schema_)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema["title"] = cls.__name__
        return json_schema

    def __repr__(self) -> str:
        """Overwrite the default representation."""
        return f"{self.__class__.__name__}({super().__str__().__repr__()})"


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
