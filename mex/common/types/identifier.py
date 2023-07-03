import re
import string
from typing import TYPE_CHECKING, Any, ClassVar
from uuid import UUID, uuid4

if TYPE_CHECKING:  # pragma: no cover
    from pydantic.typing import CallableGenerator


ALPHABET = string.ascii_letters + string.digits
MEX_ID_PATTERN = r"^[a-zA-Z0-9]{14,22}$"
UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"


class Identifier(str):
    """Common identifier class."""

    REFERENCE: ClassVar[str | None] = None

    @classmethod
    def generate(cls, seed: int | None = None) -> "Identifier":
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
    def __get_validators__(cls) -> "CallableGenerator":
        """Get all validators for this class."""
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "Identifier":
        """Validate a string, uuid or identfier."""
        if isinstance(value, (str, UUID, Identifier)):
            value = str(value)
            if re.match(MEX_ID_PATTERN, value):
                return cls(value)
            if re.match(UUID_PATTERN, value):
                return cls.generate(seed=UUID(value).int)
            raise ValueError(f"Invalid identifier format: {value}")
        raise TypeError(f"Cannot parse {type(value)} as {cls.__name__}")

    @classmethod
    def __modify_schema__(cls, field_schema: dict[str, Any]) -> None:
        """Modify the schema to add the ID regex or reference a specific ID field."""
        field_schema.clear()
        if cls.REFERENCE:
            field_schema["$ref"] = cls.REFERENCE
        else:
            field_schema.update(
                title="Identifier",
                type="string",
                pattern=MEX_ID_PATTERN,
            )

    def __repr__(self) -> str:
        """Overwrite the default representation."""
        return f"{self.__class__.__name__}({super().__str__().__repr__()})"


class AccessPlatformID(Identifier):
    """Identifier for merged access platforms."""

    REFERENCE = "#/components/schemas/AccessPlatformID"


class ActivityID(Identifier):
    """Identifier for merged activities."""

    REFERENCE = "#/components/schemas/ActivityID"


class ContactPointID(Identifier):
    """Identifier for merged contact points."""

    REFERENCE = "#/components/schemas/ContactPointID"


class DistributionID(Identifier):
    """Identifier for merged distributions."""

    REFERENCE = "#/components/schemas/DistributionID"


class OrganizationID(Identifier):
    """Identifier for merged organizations."""

    REFERENCE = "#/components/schemas/OrganizationID"


class OrganizationalUnitID(Identifier):
    """Identifier for merged organizational units."""

    REFERENCE = "#/components/schemas/OrganizationalUnitID"


class PersonID(Identifier):
    """Identifier for merged persons."""

    REFERENCE = "#/components/schemas/PersonID"


class PrimarySourceID(Identifier):
    """Identifier for merged primary sources."""

    REFERENCE = "#/components/schemas/PrimarySourceID"


class ResourceID(Identifier):
    """Identifier for merged resources."""

    REFERENCE = "#/components/schemas/ResourceID"


class VariableID(Identifier):
    """Identifier for merged variables."""

    REFERENCE = "#/components/schemas/VariableID"


class VariableGroupID(Identifier):
    """Identifier for merged variable groups."""

    REFERENCE = "#/components/schemas/VariableGroupID"
