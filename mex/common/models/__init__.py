from typing import Final, get_args

from mex.common.models.access_platform import (
    BaseAccessPlatform,
    ExtractedAccessPlatform,
    MergedAccessPlatform,
)
from mex.common.models.activity import BaseActivity, ExtractedActivity, MergedActivity
from mex.common.models.base import BaseModel
from mex.common.models.contact_point import (
    BaseContactPoint,
    ExtractedContactPoint,
    MergedContactPoint,
)
from mex.common.models.distribution import (
    BaseDistribution,
    ExtractedDistribution,
    MergedDistribution,
)
from mex.common.models.extracted_data import (
    MEX_PRIMARY_SOURCE_IDENTIFIER,
    MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE,
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    ExtractedData,
)
from mex.common.models.merged_item import MergedItem
from mex.common.models.organization import (
    BaseOrganization,
    ExtractedOrganization,
    MergedOrganization,
)
from mex.common.models.organizational_unit import (
    BaseOrganizationalUnit,
    ExtractedOrganizationalUnit,
    MergedOrganizationalUnit,
)
from mex.common.models.person import BasePerson, ExtractedPerson, MergedPerson
from mex.common.models.primary_source import (
    BasePrimarySource,
    ExtractedPrimarySource,
    MergedPrimarySource,
)
from mex.common.models.resource import BaseResource, ExtractedResource, MergedResource
from mex.common.models.variable import BaseVariable, ExtractedVariable, MergedVariable
from mex.common.models.variable_group import (
    BaseVariableGroup,
    ExtractedVariableGroup,
    MergedVariableGroup,
)

__all__ = (
    "AnyBaseModel",
    "AnyExtractedModel",
    "AnyMergedModel",
    "BASE_MODEL_CLASSES_BY_NAME",
    "BASE_MODEL_CLASSES",
    "BaseAccessPlatform",
    "BaseActivity",
    "BaseContactPoint",
    "BaseDistribution",
    "BaseModel",
    "BaseOrganization",
    "BaseOrganizationalUnit",
    "BasePerson",
    "BasePrimarySource",
    "BaseResource",
    "BaseVariable",
    "BaseVariableGroup",
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
