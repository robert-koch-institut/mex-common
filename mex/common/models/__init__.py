from typing import Final, get_args

from mex.common.models.access_platform import (
    AdditiveAccessPlatform,
    BaseAccessPlatform,
    ExtractedAccessPlatform,
    MergedAccessPlatform,
    PreventiveAccessPlatform,
    SubtractiveAccessPlatform,
)
from mex.common.models.activity import (
    AdditiveActivity,
    BaseActivity,
    ExtractedActivity,
    MergedActivity,
    PreventiveActivity,
    SubtractiveActivity,
)
from mex.common.models.base import BaseModel
from mex.common.models.contact_point import (
    AdditiveContactPoint,
    BaseContactPoint,
    ExtractedContactPoint,
    MergedContactPoint,
    PreventiveContactPoint,
    SubtractiveContactPoint,
)
from mex.common.models.distribution import (
    AdditiveDistribution,
    BaseDistribution,
    ExtractedDistribution,
    MergedDistribution,
    PreventiveDistribution,
    SubtractiveDistribution,
)
from mex.common.models.extracted_data import (
    MEX_PRIMARY_SOURCE_IDENTIFIER,
    MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE,
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    ExtractedData,
)
from mex.common.models.merged_item import MergedItem
from mex.common.models.organization import (
    AdditiveOrganization,
    BaseOrganization,
    ExtractedOrganization,
    MergedOrganization,
    PreventiveOrganization,
    SubtractiveOrganization,
)
from mex.common.models.organizational_unit import (
    AdditiveOrganizationalUnit,
    BaseOrganizationalUnit,
    ExtractedOrganizationalUnit,
    MergedOrganizationalUnit,
    PreventiveOrganizationalUnit,
    SubtractiveOrganizationalUnit,
)
from mex.common.models.person import (
    AdditivePerson,
    BasePerson,
    ExtractedPerson,
    MergedPerson,
    PreventivePerson,
    SubtractivePerson,
)
from mex.common.models.primary_source import (
    AdditivePrimarySource,
    BasePrimarySource,
    ExtractedPrimarySource,
    MergedPrimarySource,
    PreventivePrimarySource,
    SubtractivePrimarySource,
)
from mex.common.models.resource import (
    AdditiveResource,
    BaseResource,
    ExtractedResource,
    MergedResource,
    PreventiveResource,
    SubtractiveResource,
)
from mex.common.models.rule_set import AdditiveRule, PreventiveRule, SubtractiveRule
from mex.common.models.variable import (
    AdditiveVariable,
    BaseVariable,
    ExtractedVariable,
    MergedVariable,
    PreventiveVariable,
    SubtractiveVariable,
)
from mex.common.models.variable_group import (
    AdditiveVariableGroup,
    BaseVariableGroup,
    ExtractedVariableGroup,
    MergedVariableGroup,
    PreventiveVariableGroup,
    SubtractiveVariableGroup,
)

__all__ = (
    "ADDITIVE_MODEL_CLASSES_BY_NAME",
    "ADDITIVE_MODEL_CLASSES",
    "AdditiveAccessPlatform",
    "AdditiveActivity",
    "AdditiveContactPoint",
    "AdditiveDistribution",
    "AdditiveOrganization",
    "AdditiveOrganizationalUnit",
    "AdditivePerson",
    "AdditivePrimarySource",
    "AdditiveResource",
    "AdditiveRule",
    "AdditiveVariable",
    "AdditiveVariableGroup",
    "AnyAdditiveModel",
    "AnyExtractedModel",
    "AnyMergedModel",
    "AnyPreventiveModel",
    "AnySubtractiveModel",
    "BaseModel",
    "EXTRACTED_MODEL_CLASSES_BY_NAME",
    "EXTRACTED_MODEL_CLASSES",
    "ExtractedAccessPlatform",
    "ExtractedActivity",
    "ExtractedContactPoint",
    "ExtractedData",
    "ExtractedDistribution",
    "ExtractedOrganization",
    "ExtractedOrganizationalUnit",
    "ExtractedPerson",
    "ExtractedPrimarySource",
    "ExtractedResource",
    "ExtractedVariable",
    "ExtractedVariableGroup",
    "MERGED_MODEL_CLASSES_BY_NAME",
    "MERGED_MODEL_CLASSES",
    "MergedAccessPlatform",
    "MergedActivity",
    "MergedContactPoint",
    "MergedDistribution",
    "MergedItem",
    "MergedOrganization",
    "MergedOrganizationalUnit",
    "MergedPerson",
    "MergedPrimarySource",
    "MergedResource",
    "MergedVariable",
    "MergedVariableGroup",
    "MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE",
    "MEX_PRIMARY_SOURCE_IDENTIFIER",
    "MEX_PRIMARY_SOURCE_STABLE_TARGET_ID",
    "PreventiveAccessPlatform",
    "PreventiveActivity",
    "PreventiveContactPoint",
    "PreventiveDistribution",
    "PreventiveOrganization",
    "PreventiveOrganizationalUnit",
    "PreventivePerson",
    "PreventivePrimarySource",
    "PreventiveResource",
    "PreventiveRule",
    "PreventiveVariable",
    "PreventiveVariableGroup",
    "SUBTRACTIVE_MODEL_CLASSES_BY_NAME",
    "SUBTRACTIVE_MODEL_CLASSES",
    "SubtractiveAccessPlatform",
    "SubtractiveActivity",
    "SubtractiveContactPoint",
    "SubtractiveDistribution",
    "SubtractiveOrganization",
    "SubtractiveOrganizationalUnit",
    "SubtractivePerson",
    "SubtractivePrimarySource",
    "SubtractiveResource",
    "SubtractiveRule",
    "SubtractiveVariable",
    "SubtractiveVariableGroup",
)

AnyBaseModel = (
    BaseAccessPlatform
    | BaseActivity
    | BaseContactPoint
    | BaseDistribution
    | BaseOrganization
    | BaseOrganizationalUnit
    | BasePerson
    | BasePrimarySource
    | BaseResource
    | BaseVariable
    | BaseVariableGroup
)
BASE_MODEL_CLASSES: Final[list[type[AnyBaseModel]]] = list(get_args(AnyBaseModel))
BASE_MODEL_CLASSES_BY_NAME: Final[dict[str, type[AnyBaseModel]]] = {
    cls.__name__: cls for cls in BASE_MODEL_CLASSES
}

AnyExtractedModel = (
    ExtractedAccessPlatform
    | ExtractedActivity
    | ExtractedContactPoint
    | ExtractedDistribution
    | ExtractedOrganization
    | ExtractedOrganizationalUnit
    | ExtractedPerson
    | ExtractedPrimarySource
    | ExtractedResource
    | ExtractedVariable
    | ExtractedVariableGroup
)
EXTRACTED_MODEL_CLASSES: Final[list[type[AnyExtractedModel]]] = list(
    get_args(AnyExtractedModel)
)
EXTRACTED_MODEL_CLASSES_BY_NAME: Final[dict[str, type[AnyExtractedModel]]] = {
    cls.__name__: cls for cls in EXTRACTED_MODEL_CLASSES
}

AnyMergedModel = (
    MergedAccessPlatform
    | MergedActivity
    | MergedContactPoint
    | MergedDistribution
    | MergedOrganization
    | MergedOrganizationalUnit
    | MergedPerson
    | MergedPrimarySource
    | MergedResource
    | MergedVariable
    | MergedVariableGroup
)
MERGED_MODEL_CLASSES: Final[list[type[AnyMergedModel]]] = list(get_args(AnyMergedModel))
MERGED_MODEL_CLASSES_BY_NAME: Final[dict[str, type[AnyMergedModel]]] = {
    cls.__name__: cls for cls in MERGED_MODEL_CLASSES
}

AnyAdditiveModel = (
    AdditiveAccessPlatform
    | AdditiveActivity
    | AdditiveContactPoint
    | AdditiveDistribution
    | AdditiveOrganization
    | AdditiveOrganizationalUnit
    | AdditivePerson
    | AdditivePrimarySource
    | AdditiveResource
    | AdditiveVariable
    | AdditiveVariableGroup
)
ADDITIVE_MODEL_CLASSES: Final[list[type[AnyAdditiveModel]]] = list(
    get_args(AnyAdditiveModel)
)
ADDITIVE_MODEL_CLASSES_BY_NAME: Final[dict[str, type[AnyAdditiveModel]]] = {
    cls.__name__: cls for cls in ADDITIVE_MODEL_CLASSES
}

AnySubtractiveModel = (
    SubtractiveAccessPlatform
    | SubtractiveActivity
    | SubtractiveContactPoint
    | SubtractiveDistribution
    | SubtractiveOrganization
    | SubtractiveOrganizationalUnit
    | SubtractivePerson
    | SubtractivePrimarySource
    | SubtractiveResource
    | SubtractiveVariable
    | SubtractiveVariableGroup
)
SUBTRACTIVE_MODEL_CLASSES: Final[list[type[AnySubtractiveModel]]] = list(
    get_args(AnySubtractiveModel)
)
SUBTRACTIVE_MODEL_CLASSES_BY_NAME: Final[dict[str, type[AnySubtractiveModel]]] = {
    cls.__name__: cls for cls in SUBTRACTIVE_MODEL_CLASSES
}

AnyPreventiveModel = (
    PreventiveAccessPlatform
    | PreventiveActivity
    | PreventiveContactPoint
    | PreventiveDistribution
    | PreventiveOrganization
    | PreventiveOrganizationalUnit
    | PreventivePerson
    | PreventivePrimarySource
    | PreventiveResource
    | PreventiveVariable
    | PreventiveVariableGroup
)
PREVENTIVE_MODEL_CLASSES: Final[list[type[AnyPreventiveModel]]] = list(
    get_args(AnyPreventiveModel)
)
PREVENTIVE_MODEL_CLASSES_BY_NAME: Final[dict[str, type[AnyPreventiveModel]]] = {
    cls.__name__: cls for cls in PREVENTIVE_MODEL_CLASSES
}
