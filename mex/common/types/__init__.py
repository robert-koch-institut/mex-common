from typing import Final, Union, get_args

from mex.common.types.email import Email
from mex.common.types.identifier import (
    AccessPlatformID,
    ActivityID,
    ContactPointID,
    DistributionID,
    Identifier,
    OrganizationalUnitID,
    OrganizationID,
    PersonID,
    PrimarySourceID,
    ResourceID,
    VariableGroupID,
    VariableID,
)
from mex.common.types.identity import IdentityProvider
from mex.common.types.link import Link, LinkLanguage
from mex.common.types.path import AssetsPath, PathWrapper, WorkPath
from mex.common.types.sink import Sink
from mex.common.types.text import Text, TextLanguage
from mex.common.types.timestamp import (
    CET,
    TIMESTAMP_FORMATS_BY_PRECISION,
    TIMESTAMP_REGEX,
    UTC,
    Timestamp,
    TimestampPrecision,
)
from mex.common.types.vocabulary import (
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
    "AccessPlatformID",
    "AccessRestriction",
    "ActivityID",
    "ActivityType",
    "AnonymizationPseudonymization",
    "AnyNestedModel",
    "APIType",
    "AssetsPath",
    "CET",
    "ContactPointID",
    "DataProcessingState",
    "DataType",
    "DistributionID",
    "Email",
    "Frequency",
    "Identifier",
    "IdentityProvider",
    "Language",
    "License",
    "Link",
    "LinkLanguage",
    "MIMEType",
    "NESTED_MODEL_CLASSES_BY_NAME",
    "NESTED_MODEL_CLASSES",
    "OrganizationalUnitID",
    "OrganizationID",
    "PathWrapper",
    "PersonID",
    "PrimarySourceID",
    "ResourceID",
    "ResourceTypeGeneral",
    "Sink",
    "split_to_caps",
    "TechnicalAccessibility",
    "Text",
    "TextLanguage",
    "Theme",
    "TIMESTAMP_FORMATS_BY_PRECISION",
    "TIMESTAMP_REGEX",
    "Timestamp",
    "TimestampPrecision",
    "UTC",
    "VariableGroupID",
    "VariableID",
    "VocabularyEnum",
    "VocabularyLoader",
    "WorkPath",
)

AnyNestedModel = Union[
    Link,
    Text,
]
NESTED_MODEL_CLASSES: Final[list[type[AnyNestedModel]]] = list(get_args(AnyNestedModel))
NESTED_MODEL_CLASSES_BY_NAME: Final[dict[str, type[AnyNestedModel]]] = {
    cls.__name__: cls for cls in NESTED_MODEL_CLASSES
}
