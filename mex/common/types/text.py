from enum import StrEnum
from typing import Annotated, Any

from langdetect.detector_factory import PROFILES_DIRECTORY, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from pydantic import BaseModel, Field, model_validator

DETECTOR_FACTORY = DetectorFactory()
DETECTOR_FACTORY.load_profile(PROFILES_DIRECTORY)
DETECTOR_FACTORY.seed = 0


class TextLanguage(StrEnum):
    """Possible language tags for `Text` values."""

    DE = "de"
    EN = "en"


class Text(BaseModel):
    """Type class for text objects.

    Texts can be parsed from nested JSON objects or from raw strings.

    Example:
        Text(value="foo") == Text.model_validate("foo")
    """

    value: Annotated[str, Field(min_length=1)]
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

    @model_validator(mode="before")
    @classmethod
    def validate_strings(cls, value: Any) -> dict[str, Any]:  # noqa: ANN401
        """Convert string input to dictionary."""
        if isinstance(value, str):
            return {"value": value}
        if isinstance(value, dict):
            return value
        msg = f"Allowed input types are dict and str, got {type(value)}"
        raise ValueError(msg)

    def __hash__(self) -> int:
        """Return the hash of Text."""
        return hash((self.value, self.language))
