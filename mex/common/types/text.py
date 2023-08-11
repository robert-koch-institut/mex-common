from enum import Enum
from typing import Any

from langdetect.detector_factory import PROFILES_DIRECTORY, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.utils import GetterDict

DETECTOR_FACTORY = DetectorFactory()
DETECTOR_FACTORY.load_profile(PROFILES_DIRECTORY)
DETECTOR_FACTORY.seed = 0


class TextLanguage(Enum):
    """Possible language tags for `Text` values."""

    DE = "de"
    EN = "en"


class TextGetter(GetterDict):
    """Helper class to get values from a stringified Text."""

    def get(self, key: Any, default: Any = None) -> Any:
        """Get the value for the given key."""
        if key == "value":
            return self._obj
        return default


class Text(BaseModel):
    """Type class for text objects.

    Texts can be parsed from nested JSON objects or from raw strings.

    Example:
        Text(value="foo") == Text.parse_obj("foo")
    """

    # TODO[pydantic]: The following keys were removed: `getter_dict`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(from_attributes=True, getter_dict=TextGetter)

    value: str = Field(..., min_length=1)
    language: TextLanguage | None = None

    @model_validator(mode="before")
    @classmethod
    def detect_language(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Detect the language of the text if not explicitly given."""
        language = values.get("language")
        value = values.get("value")
        if value and "language" not in values:
            try:
                detector = DETECTOR_FACTORY.create()
                detector.append(value)
                language = TextLanguage(detector.detect())
            except (LangDetectException, ValueError):
                pass
        return {"language": language, "value": value}

    def __str__(self) -> str:
        """Return the text value."""
        return self.value

    def __hash__(self) -> int:
        """Return the hash of Text."""
        return hash((self.value, self.language))
