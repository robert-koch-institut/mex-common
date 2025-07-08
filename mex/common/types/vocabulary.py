from enum import Enum, EnumMeta
from typing import TYPE_CHECKING, ClassVar, Self, Union

from pydantic import (
    AnyUrl,
    BaseModel,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    json_schema,
)
from pydantic_core import core_schema

from mex.common.transform import normalize, split_to_caps
from mex.model import VOCABULARY_JSON_BY_NAME

if TYPE_CHECKING:  # pragma: no cover
    from enum import _EnumDict

    from mex.common.types import Text

VOCABULARY_PATTERN = r"https://mex.rki.de/item/[a-z0-9-]+"


class BilingualText(BaseModel):
    """String-field translated in German and English."""

    de: str | None = None
    en: str | None = None


class Concept(BaseModel):
    """Single entry in a vocabulary with stable ID, labels and definition."""

    identifier: AnyUrl
    inScheme: AnyUrl
    prefLabel: BilingualText
    altLabel: list[BilingualText] = []
    definition: BilingualText | None = None


class VocabularyLoader(EnumMeta):
    """Metaclass to load names and values from a JSON file and create a dynamic enum."""

    def __new__(
        cls, name: str, bases: tuple[type], dct: "_EnumDict"
    ) -> "VocabularyLoader":
        """Create a new enum class by loading the configured vocabulary JSON."""
        if vocabulary_name := dct.get("__vocabulary__"):
            dct["__concepts__"] = cls.parse_raw(vocabulary_name.replace("-", "_"))
            for concept in dct["__concepts__"]:
                dct[split_to_caps(concept.prefLabel.en)] = str(concept.identifier)
        return super().__new__(cls, name, bases, dct)

    @classmethod
    def parse_raw(cls, vocabulary_name: str) -> list[Concept]:
        """Parse vocabulary and return concepts as list."""
        return [
            Concept.model_validate(raw_vocabulary)
            for raw_vocabulary in VOCABULARY_JSON_BY_NAME[vocabulary_name]
        ]


class VocabularyEnum(Enum, metaclass=VocabularyLoader):
    """Base class for vocabulary enums that sets the correct metaclass."""

    __vocabulary__: ClassVar[str]
    __concepts__: ClassVar[list[Concept]]

    @classmethod
    def find(cls, search_term: Union[str, "Text"]) -> Self | None:
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
            for label in (concept.prefLabel, *concept.altLabel):
                if not label:
                    continue
                if language is None:
                    if label.de:
                        searchable_labels.append(normalize(label.de))
                    if label.en:
                        searchable_labels.append(normalize(label.en))
                elif language_label := label.model_dump().get(language.value):
                    searchable_labels.append(normalize(language_label))
            if search_term in searchable_labels:
                return cls(str(concept.identifier))
        return None

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: object, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Modify the core schema to add the vocabulary regex."""
        return core_schema.json_or_python_schema(
            json_schema=core_schema.union_schema(
                [
                    core_schema.str_schema(pattern=VOCABULARY_PATTERN),
                    core_schema.no_info_plain_validator_function(cls),
                ],
            ),
            python_schema=core_schema.chain_schema(
                [
                    core_schema.is_instance_schema(cls | str),
                    core_schema.no_info_plain_validator_function(cls),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda s: s.value,
                when_used="unless-none",
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema_: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> json_schema.JsonSchemaValue:
        """Modify the json schema to add the scheme and an example."""
        json_schema_ = handler(core_schema_)
        json_schema_["examples"] = [str(cls.__concepts__[0].identifier)]
        json_schema_["useScheme"] = f"https://mex.rki.de/item/{cls.__vocabulary__}"
        return json_schema_

    def __repr__(self) -> str:
        """Overwrite representation because dynamic enum names are unknown to mypy."""
        return f'{self.__class__.__name__}["{self.name}"]'


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


class BibliographicResourceType(VocabularyEnum):
    """The type of a bibliographic resource."""

    __vocabulary__ = "bibliographic-resource-type"


class ConsentStatus(VocabularyEnum):
    """The status of a consent."""

    __vocabulary__ = "consent-status"


class ConsentType(VocabularyEnum):
    """The type of a consent."""

    __vocabulary__ = "consent-type"


class DataProcessingState(VocabularyEnum):
    """Type for state of data processing."""

    __vocabulary__ = "data-processing-state"


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


class PersonalData(VocabularyEnum):
    """Classification of personal data."""

    __vocabulary__ = "personal-data"


class ResourceCreationMethod(VocabularyEnum):
    """The creation method of a resource."""

    __vocabulary__ = "resource-creation-method"


class ResourceTypeGeneral(VocabularyEnum):
    """The general type of a resource."""

    __vocabulary__ = "resource-type-general"


class TechnicalAccessibility(VocabularyEnum):
    """Technical accessibility within RKI and outside of RKI."""

    __vocabulary__ = "technical-accessibility"


class Theme(VocabularyEnum):
    """The theme type."""

    __vocabulary__ = "theme"
