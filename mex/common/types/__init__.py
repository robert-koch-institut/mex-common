from typing import Final, Literal, get_args

from mex.common.types.email import EMAIL_PATTERN, Email
from mex.common.types.identifier import (
    IDENTIFIER_PATTERN,
    ExtractedAccessPlatformIdentifier,
    ExtractedActivityIdentifier,
    ExtractedBibliographicResourceIdentifier,
    ExtractedConsentIdentifier,
    ExtractedContactPointIdentifier,
    ExtractedDistributionIdentifier,
    ExtractedIdentifier,
    ExtractedOrganizationalUnitIdentifier,
    ExtractedOrganizationIdentifier,
    ExtractedPersonIdentifier,
    ExtractedPrimarySourceIdentifier,
    ExtractedResourceIdentifier,
    ExtractedVariableGroupIdentifier,
    ExtractedVariableIdentifier,
    Identifier,
    MergedAccessPlatformIdentifier,
    MergedActivityIdentifier,
    MergedBibliographicResourceIdentifier,
    MergedConsentIdentifier,
    MergedContactPointIdentifier,
    MergedDistributionIdentifier,
    MergedIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedOrganizationIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
    MergedResourceIdentifier,
    MergedVariableGroupIdentifier,
    MergedVariableIdentifier,
)
from mex.common.types.identity import IdentityProvider
from mex.common.types.link import Link, LinkLanguage
from mex.common.types.path import AssetsPath, PathWrapper, WorkPath
from mex.common.types.sink import Sink
from mex.common.types.temporal_entity import (
    CET,
    TEMPORAL_ENTITY_CLASSES_BY_PRECISION,
    TEMPORAL_ENTITY_FORMATS_BY_PRECISION,
    UTC,
    TemporalEntity,
    TemporalEntityPrecision,
    Year,
    YearMonth,
    YearMonthDay,
    YearMonthDayTime,
)
from mex.common.types.text import Text, TextLanguage
from mex.common.types.validation import Validation
from mex.common.types.vocabulary import (
    VOCABULARY_PATTERN,
    AccessRestriction,
    ActivityType,
    AnonymizationPseudonymization,
    APIType,
    BibliographicResourceType,
    ConsentStatus,
    ConsentType,
    DataProcessingState,
    Frequency,
    Language,
    License,
    MIMEType,
    PersonalData,
    ResourceCreationMethod,
    ResourceTypeGeneral,
    TechnicalAccessibility,
    Theme,
    VocabularyEnum,
    VocabularyLoader,
)

__all__ = (
    "CET",
    "EMAIL_PATTERN",
    "EXTRACTED_IDENTIFIER_CLASSES",
    "EXTRACTED_IDENTIFIER_CLASSES_BY_NAME",
    "IDENTIFIER_PATTERN",
    "MERGED_IDENTIFIER_CLASSES",
    "MERGED_IDENTIFIER_CLASSES_BY_NAME",
    "NESTED_MODEL_CLASSES",
    "NESTED_MODEL_CLASSES_BY_NAME",
    "TEMPORAL_ENTITY_CLASSES_BY_PRECISION",
    "TEMPORAL_ENTITY_FORMATS_BY_PRECISION",
    "UTC",
    "VOCABULARY_ENUMS",
    "VOCABULARY_ENUMS_BY_NAME",
    "VOCABULARY_PATTERN",
    "APIType",
    "AccessRestriction",
    "ActivityType",
    "AnonymizationPseudonymization",
    "AnyExtractedIdentifier",
    "AnyMergedIdentifier",
    "AnyNestedModel",
    "AnyPrimitiveType",
    "AnyValidation",
    "AnyVocabularyEnum",
    "AssetsPath",
    "BibliographicResourceType",
    "ConsentStatus",
    "ConsentType",
    "DataProcessingState",
    "Email",
    "ExtractedAccessPlatformIdentifier",
    "ExtractedActivityIdentifier",
    "ExtractedBibliographicResourceIdentifier",
    "ExtractedConsentIdentifier",
    "ExtractedContactPointIdentifier",
    "ExtractedDistributionIdentifier",
    "ExtractedIdentifier",
    "ExtractedOrganizationIdentifier",
    "ExtractedOrganizationalUnitIdentifier",
    "ExtractedPersonIdentifier",
    "ExtractedPrimarySourceIdentifier",
    "ExtractedResourceIdentifier",
    "ExtractedVariableGroupIdentifier",
    "ExtractedVariableIdentifier",
    "Frequency",
    "Identifier",
    "IdentityProvider",
    "Language",
    "License",
    "Link",
    "LinkLanguage",
    "LiteralStringType",
    "MIMEType",
    "MergedAccessPlatformIdentifier",
    "MergedActivityIdentifier",
    "MergedBibliographicResourceIdentifier",
    "MergedConsentIdentifier",
    "MergedContactPointIdentifier",
    "MergedDistributionIdentifier",
    "MergedIdentifier",
    "MergedOrganizationIdentifier",
    "MergedOrganizationalUnitIdentifier",
    "MergedPersonIdentifier",
    "MergedPrimarySourceIdentifier",
    "MergedResourceIdentifier",
    "MergedVariableGroupIdentifier",
    "MergedVariableIdentifier",
    "PathWrapper",
    "PersonalData",
    "ResourceCreationMethod",
    "ResourceTypeGeneral",
    "Sink",
    "TechnicalAccessibility",
    "TemporalEntity",
    "TemporalEntityPrecision",
    "Text",
    "TextLanguage",
    "Theme",
    "Validation",
    "VocabularyEnum",
    "VocabularyLoader",
    "WorkPath",
    "Year",
    "YearMonth",
    "YearMonthDay",
    "YearMonthDayTime",
)

AnyVocabularyEnum = (
    AccessRestriction
    | ActivityType
    | AnonymizationPseudonymization
    | APIType
    | BibliographicResourceType
    | ConsentStatus
    | ConsentType
    | DataProcessingState
    | Frequency
    | Language
    | License
    | MIMEType
    | PersonalData
    | ResourceCreationMethod
    | ResourceTypeGeneral
    | TechnicalAccessibility
    | Theme
)
VOCABULARY_ENUMS: Final[list[type[AnyVocabularyEnum]]] = list(
    get_args(AnyVocabularyEnum)
)
VOCABULARY_ENUMS_BY_NAME: Final[dict[str, type[AnyVocabularyEnum]]] = {
    cls.__name__: cls for cls in VOCABULARY_ENUMS
}

AnyTemporalEntity = Year | YearMonth | YearMonthDay | YearMonthDayTime
TEMPORAL_ENTITIES: Final[list[type[AnyTemporalEntity]]] = list(
    get_args(AnyTemporalEntity)
)
TEMPORAL_ENTITIES_BY_NAME: Final[dict[str, type[AnyTemporalEntity]]] = {
    cls.__name__: cls for cls in TEMPORAL_ENTITIES
}

AnyNestedModel = Link | Text
NESTED_MODEL_CLASSES: Final[list[type[AnyNestedModel]]] = list(get_args(AnyNestedModel))
NESTED_MODEL_CLASSES_BY_NAME: Final[dict[str, type[AnyNestedModel]]] = {
    cls.__name__: cls for cls in NESTED_MODEL_CLASSES
}

AnyMergedIdentifier = (
    MergedAccessPlatformIdentifier
    | MergedActivityIdentifier
    | MergedBibliographicResourceIdentifier
    | MergedConsentIdentifier
    | MergedContactPointIdentifier
    | MergedDistributionIdentifier
    | MergedOrganizationalUnitIdentifier
    | MergedOrganizationIdentifier
    | MergedPersonIdentifier
    | MergedPrimarySourceIdentifier
    | MergedResourceIdentifier
    | MergedVariableGroupIdentifier
    | MergedVariableIdentifier
)
MERGED_IDENTIFIER_CLASSES: Final[list[type[AnyMergedIdentifier]]] = list(
    get_args(AnyMergedIdentifier)
)
MERGED_IDENTIFIER_CLASSES_BY_NAME: Final[dict[str, type[AnyMergedIdentifier]]] = {
    cls.__name__: cls for cls in MERGED_IDENTIFIER_CLASSES
}

AnyExtractedIdentifier = (
    ExtractedAccessPlatformIdentifier
    | ExtractedActivityIdentifier
    | ExtractedBibliographicResourceIdentifier
    | ExtractedConsentIdentifier
    | ExtractedContactPointIdentifier
    | ExtractedDistributionIdentifier
    | ExtractedOrganizationalUnitIdentifier
    | ExtractedOrganizationIdentifier
    | ExtractedPersonIdentifier
    | ExtractedPrimarySourceIdentifier
    | ExtractedResourceIdentifier
    | ExtractedVariableGroupIdentifier
    | ExtractedVariableIdentifier
)
EXTRACTED_IDENTIFIER_CLASSES: Final[list[type[AnyExtractedIdentifier]]] = list(
    get_args(AnyExtractedIdentifier)
)
EXTRACTED_IDENTIFIER_CLASSES_BY_NAME: Final[dict[str, type[AnyExtractedIdentifier]]] = {
    cls.__name__: cls for cls in EXTRACTED_IDENTIFIER_CLASSES
}

AnyValidation = Literal[Validation.STRICT, Validation.LENIENT, Validation.IGNORE]
AnyPrimitiveType = str | int | float | None | bool
LiteralStringType = type(Literal["str"])
