import re
import string
from typing import Any, Type, TypeVar
from uuid import UUID, uuid4

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

ALPHABET = string.ascii_letters + string.digits
MEX_ID_PATTERN = r"^[a-zA-Z0-9]{14,22}$"
UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

IdentifierT = TypeVar("IdentifierT", bound="Identifier")


class Identifier(str):
    """Common identifier class."""

    @classmethod
    def generate(cls: type[IdentifierT], seed: int | None = None) -> IdentifierT:
        """Generate a new identifier from a seed or random uuid version 4."""
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
    def validate(cls: type[IdentifierT], value: Any) -> IdentifierT:
        """Validate a string, uuid or identifier."""
        if isinstance(value, (str, UUID, Identifier)):
            value = str(value)
            if re.match(MEX_ID_PATTERN, value):
                return cls(value)
            if re.match(UUID_PATTERN, value):
                return cls.generate(seed=UUID(value).int)
            raise ValueError(f"Invalid identifier format: {value}")
        raise TypeError(f"Cannot parse {type(value)} as {cls.__name__}")

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        identifier_schema = {
            # "title": cls.__name__,
            "type": "str",
            "pattern": MEX_ID_PATTERN,
        }
        return core_schema.no_info_after_validator_function(
            cls.validate,
            identifier_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                str,
                info_arg=False,
                return_schema=core_schema.str_schema(),
            ),
        )

    def __repr__(self) -> str:
        """Overwrite the default representation."""
        return f"{self.__class__.__name__}({super().__str__().__repr__()})"


class AccessPlatformID(Identifier):
    """Identifier for merged access platforms."""


class ActivityID(Identifier):
    """Identifier for merged activities."""


class ContactPointID(Identifier):
    """Identifier for merged contact points."""


class DistributionID(Identifier):
    """Identifier for merged distributions."""


class OrganizationID(Identifier):
    """Identifier for merged organizations."""


class OrganizationalUnitID(Identifier):
    """Identifier for merged organizational units."""


class PersonID(Identifier):
    """Identifier for merged persons."""


class PrimarySourceID(Identifier):
    """Identifier for merged primary sources."""


class ResourceID(Identifier):
    """Identifier for merged resources."""


class VariableID(Identifier):
    """Identifier for merged variables."""


class VariableGroupID(Identifier):
    """Identifier for merged variable groups."""
