from enum import StrEnum
from functools import lru_cache
from typing import Annotated, Any

from langdetect.detector_factory import PROFILES_DIRECTORY, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from pydantic import BaseModel, Field, model_validator


@lru_cache(maxsize=1)
def get_detector_factory() -> DetectorFactory:
    """Return a detector factory with lazily loaded language profiles.

    Loading the language profiles is expensive, so it is deferred until the first
    text without an explicit language is parsed, instead of happening on import.
    """
    detector_factory = DetectorFactory()
    detector_factory.load_profile(PROFILES_DIRECTORY)
    detector_factory.seed = 0
    return detector_factory


class TextLanguage(StrEnum):
    """Possible language tags for `Text` values."""

    DE = "de"
    EN = "en"
    FR = "fr"
    ES = "es"
    RU = "ru"


class RestrictedTextLanguage(StrEnum):
    """Allows only English and German as language tags for `Text` values."""

    DE = "de"
    EN = "en"


def get_language_by_confidence(
    detector: DetectorFactory, confidence_threshold: float = 0.75
) -> TextLanguage | None:
    """Assigns None as Language if confidence is below 0.75 or is not En or DE."""
    probs = detector.get_probabilities()
    if not probs:
        return None

    best = max(probs, key=lambda p: p.prob)

    if best.prob < confidence_threshold:
        return None
    try:
        return TextLanguage(RestrictedTextLanguage(best.lang).value)
    except ValueError:
        return None


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
                detector = get_detector_factory().create()
                detector.append(value)
                language = get_language_by_confidence(detector)
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
