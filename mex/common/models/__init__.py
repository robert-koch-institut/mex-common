"""These models implement the types defined by the `mex-model` in their various stages.

The current set of entity types includes:

- AccessPlatform
- Activity
- BibliographicResource
- Consent
- ContactPoint
- Distribution
- Organization
- OrganizationalUnit
- Person
- PrimarySource
- Resource
- Variable
- VariableGroup

Each entity type `T` is modelled for the following use cases:

- `BaseT` defines all fields according to `mex-model` except for provenance fields
- `ExtractedT` defines an automatically extracted metadata item including provenance
- `MergedT` defines the result of merging extracted items and rules into a single item

- `AdditiveT` defines a rule to add values to specific fields of a merged item
- `SubtractiveT` defines a rule to subtract (or block) specific values for specific
  fields from contributing to a merged item
- `PreventiveT` defines a rule to prevent (or block) specific primary sources from
  contributing to specific fields of a merged item
- `TRuleSet` classes are used for CRUD operations on a set of three rules

- `ExtractedTEntityFilter` defines how an entity filter specification should look like
- `ExtractedTMapping` defines how a raw data to extracted item mapping should look like

Since these models for different use cases have a lot of overlapping attributes,
we use a number of intermediate private classes to compose the public classes:

- `_Stem` defines a static class attribute `stemType`, e.g. `Person` or `PrimarySource`,
  which is added to all intermediate and exported classes
- `_OptionalLists` defines all fields typed as lists with an arity of 0-n
- `_RequiredLists` defines all fields typed as lists with an arity of 1-n
- `_SparseLists` re-defines all fields from `_RequiredLists` with an arity of 0-n

- `_OptionalValues` defines all fields with optional values (arity of 0-1)
- `_RequiredValues` defines all fields with required values (arity of 1)
- `_SparseValues` re-defines all fields from `_RequiredValues` with an arity of 0-1
- `_VariadicValues` re-defines all fields from `_OptionalValues` and `_RequiredValues`
  as list fields with an arity of 0-n

- `_BaseRuleSet` bundles the additive, subtractive and preventive rules for one type

These private classes are used to compose the public classes like so:

- BaseT: _OptionalLists, _RequiredLists, _OptionalValues, _RequiredValues
- ExtractedT: BaseT, ExtractedData
- MergedT: BaseT, MergedItem

- AdditiveT: _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, AdditiveRule
- SubtractiveT: _OptionalLists, _SparseLists, _VariadicValues, SubtractiveRule
- PreventiveT: all fields from BaseT re-typed as MergedPrimarySourceIdentifier
- TRuleSetRequest: bundle of all three rules for one type used to create new rules
- TRuleSetResponse: bundle of all three rules for one type including a `stableTargetId`

- ExtractedTEntityFilter: all BaseT fields re-typed as a list of EntityFilter
- ExtractedTMapping: all BaseT fields re-typed as lists of subclasses of GenericField

In addition to the classes themselves, `mex.common.models` also exposes various
lists of models, lookups by class name and typing for unions of models.
"""

from typing import Final, get_args

from mex.common.models.access_platform import (
    AccessPlatformRuleSetRequest,
    AccessPlatformRuleSetResponse,
    AdditiveAccessPlatform,
    BaseAccessPlatform,
    ExtractedAccessPlatform,
    MergedAccessPlatform,
    PreventiveAccessPlatform,
    SubtractiveAccessPlatform,
)
from mex.common.models.activity import (
    ActivityRuleSetRequest,
    ActivityRuleSetResponse,
    AdditiveActivity,
    BaseActivity,
    ExtractedActivity,
    MergedActivity,
    PreventiveActivity,
    SubtractiveActivity,
)
from mex.common.models.base.extracted_data import ExtractedData
from mex.common.models.base.field_info import GenericFieldInfo
from mex.common.models.base.filter import generate_entity_filter_schema
from mex.common.models.base.mapping import generate_mapping_schema
from mex.common.models.base.merged_item import MergedItem
from mex.common.models.base.model import BaseModel
from mex.common.models.base.rules import AdditiveRule, PreventiveRule, SubtractiveRule
from mex.common.models.bibliographic_resource import (
    AdditiveBibliographicResource,
    BaseBibliographicResource,
    BibliographicResourceRuleSetRequest,
    BibliographicResourceRuleSetResponse,
    ExtractedBibliographicResource,
    MergedBibliographicResource,
    PreventiveBibliographicResource,
    SubtractiveBibliographicResource,
)
from mex.common.models.consent import (
    AdditiveConsent,
    BaseConsent,
    ConsentRuleSetRequest,
    ConsentRuleSetResponse,
    ExtractedConsent,
    MergedConsent,
    PreventiveConsent,
    SubtractiveConsent,
)
from mex.common.models.contact_point import (
    AdditiveContactPoint,
    BaseContactPoint,
    ContactPointRuleSetRequest,
    ContactPointRuleSetResponse,
    ExtractedContactPoint,
    MergedContactPoint,
    PreventiveContactPoint,
    SubtractiveContactPoint,
)
from mex.common.models.distribution import (
    AdditiveDistribution,
    BaseDistribution,
    DistributionRuleSetRequest,
    DistributionRuleSetResponse,
    ExtractedDistribution,
    MergedDistribution,
    PreventiveDistribution,
    SubtractiveDistribution,
)
from mex.common.models.organization import (
    AdditiveOrganization,
    BaseOrganization,
    ExtractedOrganization,
    MergedOrganization,
    OrganizationRuleSetRequest,
    OrganizationRuleSetResponse,
    PreventiveOrganization,
    SubtractiveOrganization,
)
from mex.common.models.organizational_unit import (
    AdditiveOrganizationalUnit,
    BaseOrganizationalUnit,
    ExtractedOrganizationalUnit,
    MergedOrganizationalUnit,
    OrganizationalUnitRuleSetRequest,
    OrganizationalUnitRuleSetResponse,
    PreventiveOrganizationalUnit,
    SubtractiveOrganizationalUnit,
)
from mex.common.models.person import (
    AdditivePerson,
    BasePerson,
    ExtractedPerson,
    MergedPerson,
    PersonRuleSetRequest,
    PersonRuleSetResponse,
    PreventivePerson,
    SubtractivePerson,
)
from mex.common.models.primary_source import (
    AdditivePrimarySource,
    BasePrimarySource,
    ExtractedPrimarySource,
    MergedPrimarySource,
    PreventivePrimarySource,
    PrimarySourceRuleSetRequest,
    PrimarySourceRuleSetResponse,
    SubtractivePrimarySource,
)
from mex.common.models.resource import (
    AdditiveResource,
    BaseResource,
    ExtractedResource,
    MergedResource,
    PreventiveResource,
    ResourceRuleSetRequest,
    ResourceRuleSetResponse,
    SubtractiveResource,
)
from mex.common.models.variable import (
    AdditiveVariable,
    BaseVariable,
    ExtractedVariable,
    MergedVariable,
    PreventiveVariable,
    SubtractiveVariable,
    VariableRuleSetRequest,
    VariableRuleSetResponse,
)
from mex.common.models.variable_group import (
    AdditiveVariableGroup,
    BaseVariableGroup,
    ExtractedVariableGroup,
    MergedVariableGroup,
    PreventiveVariableGroup,
    SubtractiveVariableGroup,
    VariableGroupRuleSetRequest,
    VariableGroupRuleSetResponse,
)
from mex.common.types import (
    ExtractedPrimarySourceIdentifier,
    MergedPrimarySourceIdentifier,
)

__all__ = (
    "AccessPlatformRuleSetRequest",
    "AccessPlatformRuleSetResponse",
    "ActivityRuleSetRequest",
    "ActivityRuleSetResponse",
    "ADDITIVE_MODEL_CLASSES_BY_NAME",
    "ADDITIVE_MODEL_CLASSES",
    "AdditiveAccessPlatform",
    "AdditiveActivity",
    "AdditiveBibliographicResource",
    "AdditiveConsent",
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
    "AnyBaseModel",
    "AnyExtractedModel",
    "AnyMergedModel",
    "AnyPreventiveModel",
    "AnyRuleModel",
    "AnyRuleSetRequest",
    "AnyRuleSetResponse",
    "AnySubtractiveModel",
    "BASE_MODEL_CLASSES_BY_NAME",
    "BASE_MODEL_CLASSES",
    "BaseAccessPlatform",
    "BaseActivity",
    "BaseBibliographicResource",
    "BaseConsent",
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
    "ConsentRuleSetRequest",
    "ConsentRuleSetResponse",
    "ContactPointRuleSetRequest",
    "ContactPointRuleSetResponse",
    "DistributionRuleSetRequest",
    "DistributionRuleSetResponse",
    "EXTRACTED_MODEL_CLASSES_BY_NAME",
    "EXTRACTED_MODEL_CLASSES",
    "ExtractedAccessPlatform",
    "ExtractedActivity",
    "ExtractedBibliographicResource",
    "ExtractedConsent",
    "ExtractedContactPoint",
    "ExtractedData",
    "ExtractedDistribution",
    "ExtractedOrganization",
    "ExtractedOrganizationalUnit",
    "ExtractedPerson",
    "ExtractedPrimarySource",
    "ExtractedPrimarySourceIdentifier",
    "ExtractedResource",
    "ExtractedVariable",
    "ExtractedVariableGroup",
    "FILTER_MODEL_BY_EXTRACTED_CLASS_NAME",
    "generate_entity_filter_schema",
    "generate_mapping_schema",
    "GenericFieldInfo",
    "MAPPING_MODEL_BY_EXTRACTED_CLASS_NAME",
    "MERGED_MODEL_CLASSES_BY_NAME",
    "MERGED_MODEL_CLASSES",
    "MergedAccessPlatform",
    "MergedActivity",
    "MergedBibliographicResource",
    "MergedConsent",
    "MergedContactPoint",
    "MergedDistribution",
    "MergedItem",
    "MergedOrganization",
    "MergedOrganizationalUnit",
    "MergedPerson",
    "MergedPrimarySource",
    "MergedPrimarySourceIdentifier",
    "MergedResource",
    "MergedVariable",
    "MergedVariableGroup",
    "MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE",
    "MEX_PRIMARY_SOURCE_IDENTIFIER",
    "MEX_PRIMARY_SOURCE_STABLE_TARGET_ID",
    "OrganizationalUnitRuleSetRequest",
    "OrganizationalUnitRuleSetResponse",
    "OrganizationRuleSetRequest",
    "OrganizationRuleSetResponse",
    "PersonRuleSetRequest",
    "PersonRuleSetResponse",
    "PREVENTIVE_MODEL_CLASSES_BY_NAME",
    "PREVENTIVE_MODEL_CLASSES",
    "PreventiveAccessPlatform",
    "PreventiveActivity",
    "PreventiveBibliographicResource",
    "PreventiveConsent",
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
    "PrimarySourceRuleSetRequest",
    "PrimarySourceRuleSetResponse",
    "ResourceRuleSetRequest",
    "ResourceRuleSetResponse",
    "RULE_MODEL_CLASSES_BY_NAME",
    "RULE_MODEL_CLASSES",
    "RULE_SET_REQUEST_CLASSES_BY_NAME",
    "RULE_SET_REQUEST_CLASSES",
    "RULE_SET_RESPONSE_CLASSES_BY_NAME",
    "RULE_SET_RESPONSE_CLASSES",
    "SUBTRACTIVE_MODEL_CLASSES_BY_NAME",
    "SUBTRACTIVE_MODEL_CLASSES",
    "SubtractiveAccessPlatform",
    "SubtractiveActivity",
    "SubtractiveBibliographicResource",
    "SubtractiveConsent",
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
    "VariableGroupRuleSetRequest",
    "VariableGroupRuleSetResponse",
    "VariableRuleSetRequest",
    "VariableRuleSetResponse",
)

MEX_PRIMARY_SOURCE_IDENTIFIER = ExtractedPrimarySourceIdentifier("00000000000001")
MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE = "mex"
MEX_PRIMARY_SOURCE_STABLE_TARGET_ID = MergedPrimarySourceIdentifier("00000000000000")

AnyBaseModel = (
    BaseAccessPlatform
    | BaseActivity
    | BaseBibliographicResource
    | BaseConsent
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
    | ExtractedBibliographicResource
    | ExtractedConsent
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
    | MergedBibliographicResource
    | MergedConsent
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
    | AdditiveBibliographicResource
    | AdditiveConsent
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
    | SubtractiveBibliographicResource
    | SubtractiveConsent
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
    | PreventiveBibliographicResource
    | PreventiveConsent
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

AnyRuleModel = AnyAdditiveModel | AnySubtractiveModel | AnyPreventiveModel
RULE_MODEL_CLASSES: Final[list[type[AnyRuleModel]]] = list(get_args(AnyRuleModel))
RULE_MODEL_CLASSES_BY_NAME: Final[dict[str, type[AnyRuleModel]]] = {
    cls.__name__: cls for cls in RULE_MODEL_CLASSES
}

AnyRuleSetRequest = (
    AccessPlatformRuleSetRequest
    | ActivityRuleSetRequest
    | BibliographicResourceRuleSetRequest
    | ConsentRuleSetRequest
    | ContactPointRuleSetRequest
    | DistributionRuleSetRequest
    | OrganizationRuleSetRequest
    | OrganizationalUnitRuleSetRequest
    | PersonRuleSetRequest
    | PrimarySourceRuleSetRequest
    | ResourceRuleSetRequest
    | VariableRuleSetRequest
    | VariableGroupRuleSetRequest
)
RULE_SET_REQUEST_CLASSES: Final[list[type[AnyRuleSetRequest]]] = list(
    get_args(AnyRuleSetRequest)
)
RULE_SET_REQUEST_CLASSES_BY_NAME: Final[dict[str, type[AnyRuleSetRequest]]] = {
    cls.__name__: cls for cls in RULE_SET_REQUEST_CLASSES
}

AnyRuleSetResponse = (
    AccessPlatformRuleSetResponse
    | ActivityRuleSetResponse
    | BibliographicResourceRuleSetResponse
    | ConsentRuleSetResponse
    | ContactPointRuleSetResponse
    | DistributionRuleSetResponse
    | OrganizationRuleSetResponse
    | OrganizationalUnitRuleSetResponse
    | PersonRuleSetResponse
    | PrimarySourceRuleSetResponse
    | ResourceRuleSetResponse
    | VariableRuleSetResponse
    | VariableGroupRuleSetResponse
)
RULE_SET_RESPONSE_CLASSES: Final[list[type[AnyRuleSetResponse]]] = list(
    get_args(AnyRuleSetResponse)
)
RULE_SET_RESPONSE_CLASSES_BY_NAME: Final[dict[str, type[AnyRuleSetResponse]]] = {
    cls.__name__: cls for cls in RULE_SET_RESPONSE_CLASSES
}

FILTER_MODEL_BY_EXTRACTED_CLASS_NAME = {
    cls.__name__: generate_entity_filter_schema(cls) for cls in EXTRACTED_MODEL_CLASSES
}

MAPPING_MODEL_BY_EXTRACTED_CLASS_NAME = {
    cls.__name__: generate_mapping_schema(cls) for cls in EXTRACTED_MODEL_CLASSES
}
