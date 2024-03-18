import json
import re
from enum import Enum, EnumMeta
from functools import cache
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Optional, Union

from pydantic import AnyUrl, BaseModel

from mex.common.utils import normalize

if TYPE_CHECKING:  # pragma: no cover
    from enum import _EnumDict

    from mex.common.types import Text

VOCABULARY_DIR = Path(str(files("mex.common")), "resources", "vocabularies")


class BilingualText(BaseModel):
    """String-field translated in German and English."""

    de: str
    en: str


class Concept(BaseModel):
    """Single entry in a vocabulary with stable ID, labels and definition."""

    identifier: AnyUrl
    inScheme: AnyUrl
    prefLabel: BilingualText
    altLabel: BilingualText | None = None
    definition: BilingualText | None = None


@cache
def split_to_caps(string: str) -> str:
    """Convert the given string from `Split case` into `CAPS_CASE`."""
    return "_".join(word.upper() for word in re.split("[^a-zA-Z]", string) if word)


class VocabularyLoader(EnumMeta):
    """Metaclass to load names and values from a JSON file and create a dynamic enum."""

    def __new__(
        cls: type["VocabularyLoader"], name: str, bases: tuple[type], dct: "_EnumDict"
    ) -> "VocabularyLoader":
        """Create a new enum class by loading the configured vocabulary JSON."""
        if vocabulary_name := dct.get("__vocabulary__"):
            dct["__concepts__"] = cls.parse_file(
                VOCABULARY_DIR / f"{vocabulary_name}.json"
            )
            for concept in dct["__concepts__"]:
                dct[split_to_caps(concept.prefLabel.en)] = str(concept.identifier)
        return super().__new__(cls, name, bases, dct)

    @classmethod
    def parse_file(cls, path: Path) -> list[Concept]:
        """Parse vocabulary file and return concepts as list."""
        with open(path) as handle:
            raw_vocabularies = json.load(handle)
        return [
            Concept.model_validate(raw_vocabulary)
            for raw_vocabulary in raw_vocabularies
        ]


class VocabularyEnum(Enum, metaclass=VocabularyLoader):
    """Base class for vocabulary enums that sets the correct metaclass."""

    __vocabulary__: ClassVar[str]
    __concepts__: ClassVar[list[Concept]]

    def __repr__(self) -> str:
        """Overwrite representation because dynamic enum names are unknown to mypy."""
        return f'{self.__class__.__name__}["{self.name}"]'

    @classmethod
    def find(cls, search_term: Union[str, "Text"]) -> Optional["VocabularyEnum"]:
        """Get the enum instance that matches a label of the underlying concepts.

        The given `search_term` can be string or a Text with an optional language
        setting to narrow down the search fields.
        The `prefLabel` and `altLabel` of the concepts which were used to create this
        vocabulary are searched for exact matches to the `search_term`.

        Args:
            search_term: String or Text to look for

        Returns:
            Enum instance for the found concept or None
        """
        language = getattr(search_term, "language", None)
        search_term = normalize(str(search_term))
        for concept in cls.__concepts__:
            searchable_labels = []
            for label in (concept.prefLabel, concept.altLabel):
                if not label:
                    continue
                if language is None:
                    searchable_labels.extend([normalize(label.de), normalize(label.en)])
                elif language_label := label.dict().get(language.value):
                    searchable_labels.append(normalize(language_label))
            if search_term in searchable_labels:
                return cls(str(concept.identifier))
        return None


class AccessRestriction(VocabularyEnum):
    """The access restriction type."""

    __vocabulary__ = "access-restriction"


class ActivityType(VocabularyEnum):
    """The activity type."""

    __vocabulary__ = "activity-type"


class AnonymizationPseudonymization(VocabularyEnum):
    """Whether the resource is anonymized/pseudonymized."""

    __vocabulary__ = "anonymization-pseudonymization"


class APIType(VocabularyEnum):
    """Technical standard or style of a network API."""

    __vocabulary__ = "api-type"


class DataProcessingState(VocabularyEnum):
    """Type for state of data processing."""

    __vocabulary__ = "data-processing-state"


class DataType(VocabularyEnum):
    """The type of the single piece of information within a datum."""

    __vocabulary__ = "data-type"


class Frequency(VocabularyEnum):
    """Frequency type."""

    __vocabulary__ = "frequency"


class Language(VocabularyEnum):
    """Language type."""

    __vocabulary__ = "language"


class License(VocabularyEnum):
    """License type."""

    __vocabulary__ = "license"


class MIMEType(VocabularyEnum):
    """The mime type."""

    __vocabulary__ = "mime-type"


class ResourceTypeGeneral(VocabularyEnum):
    """The general type of a resource."""

    __vocabulary__ = "resource-type-general"


class TechnicalAccessibility(VocabularyEnum):
    """Technical accessibility within RKI and outside of RKI."""

    __vocabulary__ = "technical-accessibility"


class Theme(VocabularyEnum):
    """The theme type."""

    __vocabulary__ = "theme"
