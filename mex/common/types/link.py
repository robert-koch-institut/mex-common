from enum import StrEnum
from typing import Annotated, Any

from pydantic import BaseModel, Field, model_validator

URL_PATTERN = (
    "^(?:(?:[^:/?#]+):)?(?://(?:[^/?#]*))?(?:[^?#]*)(?:\\?(?:[^#]*))?(?:#(?:.*))?$"
)


class LinkLanguage(StrEnum):
    """Possible language tags for `Link` values."""

    DE = "de"
    EN = "en"


class Link(BaseModel):
    """Type class for Link objects.

    Links can be parsed from nested JSON objects or from raw strings.

    Example:
        Link(url="http://foo.bar") == Link.model_validate("http://foo.bar")
    """

    language: LinkLanguage | None = None
    title: str | None = None
    url: Annotated[
        str,
        Field(
            pattern=URL_PATTERN,
            min_length=1,
            examples=["https://hello-world.org", "file://S:/OE/MF4/Projekte/MEx"],
            json_schema_extra={"format": "uri"},
        ),
    ]

    @model_validator(mode="before")
    @classmethod
    def validate_strings(cls, value: Any) -> dict[str, Any]:  # noqa: ANN401
        """Convert string input to dictionary."""
        if isinstance(value, str):
            return {"url": value}
        if isinstance(value, dict):
            return value
        msg = f"Allowed input types are dict and str, got {type(value)}"
        raise ValueError(msg)

    def __hash__(self) -> int:
        """Return the hash of this link."""
        return hash((self.url, self.title, self.language))
