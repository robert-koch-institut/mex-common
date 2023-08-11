import re
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.utils import GetterDict

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


class LinkLanguage(Enum):
    """Possible language tags for `Link` values."""

    DE = "de"
    EN = "en"


class LinkGetter(GetterDict):
    """Helper class to get values from a markdown Link."""

    def get(self, key: Any, default: Any = None) -> Any:
        """Get the value for the given key."""
        if match := re.match(r"\[(?P<title>.*)\]\((?P<url>.*)\)", self._obj):
            values = {
                key: markdown_unescape(value)
                for key, value in match.groupdict().items()
            }
        else:
            values = {"url": self._obj}

        return values.get(key, default)


class Link(BaseModel):
    """Type class for Link objects.

    Links can be parsed from nested JSON objects or from markdown strings.

    Example:
        Link(url="https://foo", title="Title") == Link.parse_obj("[Title](https://foo)")
    """

    # TODO[pydantic]: The following keys were removed: `getter_dict`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(from_attributes=True, getter_dict=LinkGetter)

    language: LinkLanguage | None = None
    title: str | None = None
    url: str = Field(
        ...,
        pattern=r"^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\\?([^#]*))?(#(.*))?",
        min_length=1,
        format="uri",
        examples=["https://hello-world.org", "file://S:/OE/MF4/Projekte/MEx"],
    )

    def __str__(self) -> str:
        """Render the link as markdown if a title is set, otherwise as plain url."""
        if title := self.title:
            title = markdown_escape(title)
            url = markdown_escape(self.url)
            return f"[{title}]({url})"
        else:
            return self.url
