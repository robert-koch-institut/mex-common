from typing import Final, Literal, get_args

from mex.common.types.email import EMAIL_PATTERN, Email
from mex.common.types.identifier import (
    IDENTIFIER_PATTERN,
    ExtractedAccessPlatformIdentifier,
    ExtractedActivityIdentifier,
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
    YearMonth,
    YearMonthDay,
    YearMonthDayTime,
)
from mex.common.types.text import Text, TextLanguage
from mex.common.types.vocabulary import (
    VOCABULARY_PATTERN,
    AccessRestriction,
    ActivityType,
    AnonymizationPseudonymization,
    APIType,
    DataProcessingState,
    DataType,
    Frequency,
    Language,
    License,
    MIMEType,
    ResourceTypeGeneral,
    TechnicalAccessibility,
    Theme,
    VocabularyEnum,
    VocabularyLoader,
    split_to_caps,
)

__all__ = (
    "AccessRestriction",
    "ActivityType",
    "AnonymizationPseudonymization",
    "AnyExtractedIdentifier",
    "AnyMergedIdentifier",
    "AnyNestedModel",
    "AnyPrimitiveType",
    "APIType",
    "AssetsPath",
    "CET",
    "DataProcessingState",
    "DataType",
    "EMAIL_PATTERN",
    "Email",
    "EXTRACTED_IDENTIFIER_CLASSES_BY_NAME",
    "EXTRACTED_IDENTIFIER_CLASSES",
    "ExtractedAccessPlatformIdentifier",
    "ExtractedActivityIdentifier",
    "ExtractedContactPointIdentifier",
    "ExtractedDistributionIdentifier",
    "ExtractedIdentifier",
    "ExtractedOrganizationalUnitIdentifier",
    "ExtractedOrganizationIdentifier",
    "ExtractedPersonIdentifier",
    "ExtractedPrimarySourceIdentifier",
    "ExtractedResourceIdentifier",
    "ExtractedVariableGroupIdentifier",
    "ExtractedVariableIdentifier",
    "Frequency",
    "IDENTIFIER_PATTERN",
    "Identifier",
    "IdentityProvider",
    "Language",
    "License",
    "Link",
    "LinkLanguage",
    "LiteralStringType",
    "MERGED_IDENTIFIER_CLASSES_BY_NAME",
    "MERGED_IDENTIFIER_CLASSES",
    "MergedAccessPlatformIdentifier",
    "MergedActivityIdentifier",
    "MergedContactPointIdentifier",
    "MergedDistributionIdentifier",
    "MergedIdentifier",
    "MergedOrganizationalUnitIdentifier",
    "MergedOrganizationIdentifier",
    "MergedPersonIdentifier",
    "MergedPrimarySourceIdentifier",
    "MergedResourceIdentifier",
    "MergedVariableGroupIdentifier",
    "MergedVariableIdentifier",
    "MIMEType",
    "NESTED_MODEL_CLASSES_BY_NAME",
    "NESTED_MODEL_CLASSES",
    "PathWrapper",
    "ResourceTypeGeneral",
    "Sink",
    "split_to_caps",
    "TechnicalAccessibility",
    "TEMPORAL_ENTITY_CLASSES_BY_PRECISION",
    "TEMPORAL_ENTITY_FORMATS_BY_PRECISION",
    "TemporalEntity",
    "TemporalEntityPrecision",
    "Text",
    "TextLanguage",
    "Theme",
    "URL_PATTERN",
    "UTC",
    "VOCABULARY_PATTERN",
    "VocabularyEnum",
    "VocabularyLoader",
    "WorkPath",
    "YearMonth",
    "YearMonthDay",
    "YearMonthDayTime",
)

AnyNestedModel = Link | Text
NESTED_MODEL_CLASSES: Final[list[type[AnyNestedModel]]] = list(get_args(AnyNestedModel))
NESTED_MODEL_CLASSES_BY_NAME: Final[dict[str, type[AnyNestedModel]]] = {
    cls.__name__: cls for cls in NESTED_MODEL_CLASSES
}

AnyMergedIdentifier = (
    MergedAccessPlatformIdentifier
    | MergedActivityIdentifier
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

AnyPrimitiveType = str | int | float | None | bool
LiteralStringType = type(Literal["str"])
