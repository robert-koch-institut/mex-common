from typing import Final

from mex.common.models.access_platform import ExtractedAccessPlatform
from mex.common.models.activity import ExtractedActivity
from mex.common.models.base import BaseModel, MExModel
from mex.common.models.contact_point import ExtractedContactPoint
from mex.common.models.distribution import ExtractedDistribution
from mex.common.models.organization import ExtractedOrganization
from mex.common.models.organizational_unit import ExtractedOrganizationalUnit
from mex.common.models.person import ExtractedPerson
from mex.common.models.primary_source import ExtractedPrimarySource
from mex.common.models.resource import ExtractedResource
from mex.common.models.variable import ExtractedVariable
from mex.common.models.variable_group import ExtractedVariableGroup

__all__ = (
    "BaseModel",
    "ExtractedAccessPlatform",
    "ExtractedActivity",
    "ExtractedContactPoint",
    "ExtractedDistribution",
    "ExtractedOrganization",
    "ExtractedOrganizationalUnit",
    "ExtractedPerson",
    "ExtractedPrimarySource",
    "ExtractedResource",
    "ExtractedVariable",
    "ExtractedVariableGroup",
    "MExModel",
)

MODEL_CLASSES: Final[list[type[MExModel]]] = [
    ExtractedAccessPlatform,
    ExtractedActivity,
    ExtractedContactPoint,
    ExtractedDistribution,
    ExtractedOrganization,
    ExtractedOrganizationalUnit,
    ExtractedPerson,
    ExtractedPrimarySource,
    ExtractedResource,
    ExtractedVariable,
    ExtractedVariableGroup,
]

MODEL_CLASSES_BY_ENTITY_TYPE: Final[dict[str, type[MExModel]]] = {
    cls.get_entity_type(): cls for cls in MODEL_CLASSES
}
