import re
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

# https://daringfireball.net/projects/markdown/syntax#backslash
MARKDOWN_SPECIAL_CHARS = r"\`*_{}[]()#+-.!"


def markdown_escape(string: str) -> str:
    """Escape all special characters for markdown usage."""
    for char in MARKDOWN_SPECIAL_CHARS:
        string = string.replace(char, f"\\{char}")
    return string


def markdown_unescape(string: str) -> str:
    """Unescape all special characters from a markdown string."""
    for char in MARKDOWN_SPECIAL_CHARS:
        string = string.replace(f"\\{char}", char)
    return string


class LinkLanguage(StrEnum):
    """Possible language tags for `Link` values."""

    DE = "de"
    EN = "en"


class Link(BaseModel):
    """Type class for Link objects.

    Links can be parsed from nested JSON objects or from markdown strings.

    Example:
        Link(url="https://foo", title="Title") == Link.model_validate("[Title](https://foo)")
    """

    language: LinkLanguage | None = None
    title: str | None = None
    url: str = Field(
        ...,
        pattern=r"^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\\?([^#]*))?(#(.*))?",
        min_length=1,
        examples=["https://hello-world.org", "file://S:/OE/MF4/Projekte/MEx"],
        json_schema_extra={"format": "uri"},
    )

    @model_validator(mode="before")
    @classmethod
    def convert_markdown_to_link(cls, values: Any) -> dict[str, Any]:
        """Convert string input to dictionary."""
        if isinstance(values, dict):
            return values
        elif isinstance(values, str):
            if match := re.match(r"\[(?P<title>.*)\]\((?P<url>.*)\)", values):
                url_dict = {
                    key: markdown_unescape(value)
                    for key, value in match.groupdict().items()
                }
            else:
                url_dict = {"url": values}

            return url_dict
        else:
            raise ValueError(
                f"Allowed input types are dict and str, got {type(values)}"
            )

    def __str__(self) -> str:
        """Render the link as markdown if a title is set, otherwise as plain url."""
        if title := self.title:
            title = markdown_escape(title)
            url = markdown_escape(self.url)
            return f"[{title}]({url})"
        else:
            return self.url
