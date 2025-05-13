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
- `PreviewT` defines a preview of a merged item without enforcing cardinality validation

- `AdditiveT` defines a rule to add values to specific fields of a merged item
- `SubtractiveT` defines a rule to subtract (or block) specific values for specific
  fields from contributing to a merged item
- `PreventiveT` defines a rule to prevent (or block) specific primary sources from
  contributing to specific fields of a merged item
- `TRuleSet` classes are used for CRUD operations on a set of three rules

- `TFilter` defines how an entity filter specification should look like
- `TMapping` defines how a raw-data to extracted item mapping should look like

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
- PreviewT: _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, PreviewItem

- AdditiveT: _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, AdditiveRule
- SubtractiveT: _OptionalLists, _SparseLists, _VariadicValues, SubtractiveRule
- PreventiveT: all fields from BaseT re-typed as MergedPrimarySourceIdentifier
- TRuleSetRequest: bundle of all three rules for one type used to create new rules
- TRuleSetResponse: bundle of all three rules for one type including a `stableTargetId`

- TFilter: a single field containing a list of filter rule definitions
- TMapping: all BaseT fields re-typed as lists of mapping fields with `setValues` type

All models intended for developer consumption have two main classifying class variables:
The frozen `entityType` field is added to classes to help with assigning the correct
class when reading raw JSON entities. Simple duck-typing would not work, because some
entity-types have overlapping attributes, like `Person.email` and `ContactPoint.email`.
See: https://docs.pydantic.dev/latest/concepts/fields/#discriminator
The frozen `stemType` class variable is added to classes to help with knowing which
special-use-case classes are meant for the same type of items.
E.g. `ExtractedPerson`, `MergedPerson` and `PreventivePerson` all share the same
`stemType` of `"Person"`.

In addition to the classes themselves, `mex.common.models` also exposes various
lists of models, lookups by class name and typing for unions of models.
"""

from typing import Annotated, Final, get_args

from pydantic import Field, TypeAdapter

from mex.common.models.access_platform import (
    AccessPlatformFilter,
    AccessPlatformMapping,
    AccessPlatformRuleSetRequest,
    AccessPlatformRuleSetResponse,
    AdditiveAccessPlatform,
    BaseAccessPlatform,
    ExtractedAccessPlatform,
    MergedAccessPlatform,
    PreventiveAccessPlatform,
    PreviewAccessPlatform,
    SubtractiveAccessPlatform,
)
from mex.common.models.activity import (
    ActivityFilter,
    ActivityMapping,
    ActivityRuleSetRequest,
    ActivityRuleSetResponse,
    AdditiveActivity,
    BaseActivity,
    ExtractedActivity,
    MergedActivity,
    PreventiveActivity,
    PreviewActivity,
    SubtractiveActivity,
)
from mex.common.models.base.container import (
    ItemsContainer,
    PaginatedItemsContainer,
)
from mex.common.models.base.extracted_data import ExtractedData
from mex.common.models.base.filter import BaseFilter, FilterField, FilterRule
from mex.common.models.base.mapping import BaseMapping, MappingField, MappingRule
from mex.common.models.base.merged_item import MergedItem
from mex.common.models.base.model import BaseModel
from mex.common.models.base.rules import AdditiveRule, PreventiveRule, SubtractiveRule
from mex.common.models.bibliographic_resource import (
    AdditiveBibliographicResource,
    BaseBibliographicResource,
    BibliographicResourceFilter,
    BibliographicResourceMapping,
    BibliographicResourceRuleSetRequest,
    BibliographicResourceRuleSetResponse,
    ExtractedBibliographicResource,
    MergedBibliographicResource,
    PreventiveBibliographicResource,
    PreviewBibliographicResource,
    SubtractiveBibliographicResource,
)
from mex.common.models.consent import (
    AdditiveConsent,
    BaseConsent,
    ConsentFilter,
    ConsentMapping,
    ConsentRuleSetRequest,
    ConsentRuleSetResponse,
    ExtractedConsent,
    MergedConsent,
    PreventiveConsent,
    PreviewConsent,
    SubtractiveConsent,
)
from mex.common.models.contact_point import (
    AdditiveContactPoint,
    BaseContactPoint,
    ContactPointFilter,
    ContactPointMapping,
    ContactPointRuleSetRequest,
    ContactPointRuleSetResponse,
    ExtractedContactPoint,
    MergedContactPoint,
    PreventiveContactPoint,
    PreviewContactPoint,
    SubtractiveContactPoint,
)
from mex.common.models.distribution import (
    AdditiveDistribution,
    BaseDistribution,
    DistributionFilter,
    DistributionMapping,
    DistributionRuleSetRequest,
    DistributionRuleSetResponse,
    ExtractedDistribution,
    MergedDistribution,
    PreventiveDistribution,
    PreviewDistribution,
    SubtractiveDistribution,
)
from mex.common.models.organization import (
    AdditiveOrganization,
    BaseOrganization,
    ExtractedOrganization,
    MergedOrganization,
    OrganizationFilter,
    OrganizationMapping,
    OrganizationRuleSetRequest,
    OrganizationRuleSetResponse,
    PreventiveOrganization,
    PreviewOrganization,
    SubtractiveOrganization,
)
from mex.common.models.organizational_unit import (
    AdditiveOrganizationalUnit,
    BaseOrganizationalUnit,
    ExtractedOrganizationalUnit,
    MergedOrganizationalUnit,
    OrganizationalUnitFilter,
    OrganizationalUnitMapping,
    OrganizationalUnitRuleSetRequest,
    OrganizationalUnitRuleSetResponse,
    PreventiveOrganizationalUnit,
    PreviewOrganizationalUnit,
    SubtractiveOrganizationalUnit,
)
from mex.common.models.person import (
    AdditivePerson,
    BasePerson,
    ExtractedPerson,
    MergedPerson,
    PersonFilter,
    PersonMapping,
    PersonRuleSetRequest,
    PersonRuleSetResponse,
    PreventivePerson,
    PreviewPerson,
    SubtractivePerson,
)
from mex.common.models.primary_source import (
    AdditivePrimarySource,
    BasePrimarySource,
    ExtractedPrimarySource,
    MergedPrimarySource,
    PreventivePrimarySource,
    PreviewPrimarySource,
    PrimarySourceFilter,
    PrimarySourceMapping,
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
    PreviewResource,
    ResourceFilter,
    ResourceMapping,
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
    PreviewVariable,
    SubtractiveVariable,
    VariableFilter,
    VariableMapping,
    VariableRuleSetRequest,
    VariableRuleSetResponse,
)
from mex.common.models.variable_group import (
    AdditiveVariableGroup,
    BaseVariableGroup,
    ExtractedVariableGroup,
    MergedVariableGroup,
    PreventiveVariableGroup,
    PreviewVariableGroup,
    SubtractiveVariableGroup,
    VariableGroupFilter,
    VariableGroupMapping,
    VariableGroupRuleSetRequest,
    VariableGroupRuleSetResponse,
)
from mex.common.types import (
    ExtractedPrimarySourceIdentifier,
    MergedPrimarySourceIdentifier,
)

__all__ = (
    "ADDITIVE_MODEL_CLASSES",
    "ADDITIVE_MODEL_CLASSES_BY_NAME",
    "BASE_MODEL_CLASSES",
    "BASE_MODEL_CLASSES_BY_NAME",
    "EXTRACTED_MODEL_CLASSES",
    "EXTRACTED_MODEL_CLASSES_BY_NAME",
    "FILTER_MODEL_BY_EXTRACTED_CLASS_NAME",
    "MAPPING_MODEL_BY_EXTRACTED_CLASS_NAME",
    "MERGED_MODEL_CLASSES",
    "MERGED_MODEL_CLASSES_BY_NAME",
    "MEX_PRIMARY_SOURCE_IDENTIFIER",
    "MEX_PRIMARY_SOURCE_IDENTIFIER_IN_PRIMARY_SOURCE",
    "MEX_PRIMARY_SOURCE_STABLE_TARGET_ID",
    "PREVENTIVE_MODEL_CLASSES",
    "PREVENTIVE_MODEL_CLASSES_BY_NAME",
    "RULE_MODEL_CLASSES",
    "RULE_MODEL_CLASSES_BY_NAME",
    "RULE_SET_REQUEST_CLASSES",
    "RULE_SET_REQUEST_CLASSES_BY_NAME",
    "RULE_SET_RESPONSE_CLASSES",
    "RULE_SET_RESPONSE_CLASSES_BY_NAME",
    "SUBTRACTIVE_MODEL_CLASSES",
    "SUBTRACTIVE_MODEL_CLASSES_BY_NAME",
    "AccessPlatformFilter",
    "AccessPlatformMapping",
    "AccessPlatformRuleSetRequest",
    "AccessPlatformRuleSetResponse",
    "ActivityFilter",
    "ActivityMapping",
    "ActivityRuleSetRequest",
    "ActivityRuleSetResponse",
    "AdditiveAccessPlatform",
    "AdditiveActivity",
    "AdditiveBibliographicResource",
    "AdditiveConsent",
    "AdditiveContactPoint",
    "AdditiveDistribution",
    "AdditiveModelTypeAdapter",
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
    "AnyPreviewModel",
    "AnyRuleModel",
    "AnyRuleSetRequest",
    "AnyRuleSetResponse",
    "AnySubtractiveModel",
    "BaseAccessPlatform",
    "BaseActivity",
    "BaseBibliographicResource",
    "BaseConsent",
    "BaseContactPoint",
    "BaseDistribution",
    "BaseFilter",
    "BaseMapping",
    "BaseModel",
    "BaseOrganization",
    "BaseOrganizationalUnit",
    "BasePerson",
    "BasePrimarySource",
    "BaseResource",
    "BaseVariable",
    "BaseVariableGroup",
    "BibliographicResourceFilter",
    "BibliographicResourceMapping",
    "ConsentFilter",
    "ConsentMapping",
    "ConsentRuleSetRequest",
    "ConsentRuleSetResponse",
    "ContactPointFilter",
    "ContactPointMapping",
    "ContactPointRuleSetRequest",
    "ContactPointRuleSetResponse",
    "DistributionFilter",
    "DistributionMapping",
    "DistributionRuleSetRequest",
    "DistributionRuleSetResponse",
    "ExtractedAccessPlatform",
    "ExtractedActivity",
    "ExtractedBibliographicResource",
    "ExtractedConsent",
    "ExtractedContactPoint",
    "ExtractedData",
    "ExtractedDistribution",
    "ExtractedModelTypeAdapter",
    "ExtractedOrganization",
    "ExtractedOrganizationalUnit",
    "ExtractedPerson",
    "ExtractedPrimarySource",
    "ExtractedResource",
    "ExtractedVariable",
    "ExtractedVariableGroup",
    "FilterField",
    "FilterModelTypeAdapter",
    "FilterRule",
    "ItemsContainer",
    "MappingField",
    "MappingModelTypeAdapter",
    "MappingRule",
    "MergedAccessPlatform",
    "MergedActivity",
    "MergedBibliographicResource",
    "MergedConsent",
    "MergedContactPoint",
    "MergedDistribution",
    "MergedItem",
    "MergedModelTypeAdapter",
    "MergedOrganization",
    "MergedOrganizationalUnit",
    "MergedPerson",
    "MergedPrimarySource",
    "MergedResource",
    "MergedVariable",
    "MergedVariableGroup",
    "OrganizationFilter",
    "OrganizationMapping",
    "OrganizationRuleSetRequest",
    "OrganizationRuleSetResponse",
    "OrganizationalUnitFilter",
    "OrganizationalUnitMapping",
    "OrganizationalUnitRuleSetRequest",
    "OrganizationalUnitRuleSetResponse",
    "PaginatedItemsContainer",
    "PersonFilter",
    "PersonMapping",
    "PersonRuleSetRequest",
    "PersonRuleSetResponse",
    "PreventiveAccessPlatform",
    "PreventiveActivity",
    "PreventiveBibliographicResource",
    "PreventiveConsent",
    "PreventiveContactPoint",
    "PreventiveDistribution",
    "PreventiveModelTypeAdapter",
    "PreventiveOrganization",
    "PreventiveOrganizationalUnit",
    "PreventivePerson",
    "PreventivePrimarySource",
    "PreventiveResource",
    "PreventiveRule",
    "PreventiveVariable",
    "PreventiveVariableGroup",
    "PreviewAccessPlatform",
    "PreviewActivity",
    "PreviewBibliographicResource",
    "PreviewConsent",
    "PreviewContactPoint",
    "PreviewDistribution",
    "PreviewModelTypeAdapter",
    "PreviewOrganization",
    "PreviewOrganizationalUnit",
    "PreviewPerson",
    "PreviewPrimarySource",
    "PreviewResource",
    "PreviewVariable",
    "PreviewVariableGroup",
    "PrimarySourceFilter",
    "PrimarySourceMapping",
    "PrimarySourceRuleSetRequest",
    "PrimarySourceRuleSetResponse",
    "ResourceFilter",
    "ResourceMapping",
    "ResourceRuleSetRequest",
    "ResourceRuleSetResponse",
    "RuleModelTypeAdapter",
    "RuleSetRequestTypeAdapter",
    "RuleSetResponseTypeAdapter",
    "SubtractiveAccessPlatform",
    "SubtractiveActivity",
    "SubtractiveBibliographicResource",
    "SubtractiveConsent",
    "SubtractiveContactPoint",
    "SubtractiveDistribution",
    "SubtractiveModelTypeAdapter",
    "SubtractiveOrganization",
    "SubtractiveOrganizationalUnit",
    "SubtractivePerson",
    "SubtractivePrimarySource",
    "SubtractiveResource",
    "SubtractiveRule",
    "SubtractiveVariable",
    "SubtractiveVariableGroup",
    "VariableFilter",
    "VariableGroupFilter",
    "VariableGroupMapping",
    "VariableGroupRuleSetRequest",
    "VariableGroupRuleSetResponse",
    "VariableMapping",
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
ExtractedModelTypeAdapter: TypeAdapter[AnyExtractedModel] = TypeAdapter(
    Annotated[AnyExtractedModel, Field(discriminator="entityType")]
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
MergedModelTypeAdapter: TypeAdapter[AnyMergedModel] = TypeAdapter(
    Annotated[AnyMergedModel, Field(discriminator="entityType")]
)
MERGED_MODEL_CLASSES: Final[list[type[AnyMergedModel]]] = list(get_args(AnyMergedModel))
MERGED_MODEL_CLASSES_BY_NAME: Final[dict[str, type[AnyMergedModel]]] = {
    cls.__name__: cls for cls in MERGED_MODEL_CLASSES
}

AnyPreviewModel = (
    PreviewAccessPlatform
    | PreviewActivity
    | PreviewBibliographicResource
    | PreviewConsent
    | PreviewContactPoint
    | PreviewDistribution
    | PreviewOrganization
    | PreviewOrganizationalUnit
    | PreviewPerson
    | PreviewPrimarySource
    | PreviewResource
    | PreviewVariable
    | PreviewVariableGroup
)
PreviewModelTypeAdapter: TypeAdapter[AnyPreviewModel] = TypeAdapter(
    Annotated[AnyPreviewModel, Field(discriminator="entityType")]
)
PREVIEW_MODEL_CLASSES: Final[list[type[AnyPreviewModel]]] = list(
    get_args(AnyPreviewModel)
)
PREVIEW_MODEL_CLASSES_BY_NAME: Final[dict[str, type[AnyPreviewModel]]] = {
    cls.__name__: cls for cls in PREVIEW_MODEL_CLASSES
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
AdditiveModelTypeAdapter: TypeAdapter[AnyAdditiveModel] = TypeAdapter(
    Annotated[AnyAdditiveModel, Field(discriminator="entityType")]
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
SubtractiveModelTypeAdapter: TypeAdapter[AnySubtractiveModel] = TypeAdapter(
    Annotated[AnySubtractiveModel, Field(discriminator="entityType")]
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
PreventiveModelTypeAdapter: TypeAdapter[AnyPreventiveModel] = TypeAdapter(
    Annotated[AnyPreventiveModel, Field(discriminator="entityType")]
)
PREVENTIVE_MODEL_CLASSES: Final[list[type[AnyPreventiveModel]]] = list(
    get_args(AnyPreventiveModel)
)
PREVENTIVE_MODEL_CLASSES_BY_NAME: Final[dict[str, type[AnyPreventiveModel]]] = {
    cls.__name__: cls for cls in PREVENTIVE_MODEL_CLASSES
}

AnyRuleModel = AnyAdditiveModel | AnySubtractiveModel | AnyPreventiveModel
RuleModelTypeAdapter: TypeAdapter[AnyRuleModel] = TypeAdapter(
    Annotated[AnyRuleModel, Field(discriminator="entityType")]
)
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
RuleSetRequestTypeAdapter: TypeAdapter[AnyRuleSetRequest] = TypeAdapter(
    Annotated[AnyRuleSetRequest, Field(discriminator="entityType")]
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
RuleSetResponseTypeAdapter: TypeAdapter[AnyRuleSetResponse] = TypeAdapter(
    Annotated[AnyRuleSetResponse, Field(discriminator="entityType")]
)
RULE_SET_RESPONSE_CLASSES: Final[list[type[AnyRuleSetResponse]]] = list(
    get_args(AnyRuleSetResponse)
)
RULE_SET_RESPONSE_CLASSES_BY_NAME: Final[dict[str, type[AnyRuleSetResponse]]] = {
    cls.__name__: cls for cls in RULE_SET_RESPONSE_CLASSES
}

AnyMappingModel = (
    AccessPlatformMapping
    | ActivityMapping
    | BibliographicResourceMapping
    | ConsentMapping
    | ContactPointMapping
    | DistributionMapping
    | OrganizationMapping
    | OrganizationalUnitMapping
    | PersonMapping
    | PrimarySourceMapping
    | ResourceMapping
    | VariableMapping
    | VariableGroupMapping
)
MappingModelTypeAdapter: TypeAdapter[AnyMappingModel] = TypeAdapter(
    Annotated[AnyMappingModel, Field(discriminator="entityType")]
)
MAPPING_MODEL_CLASSES: Final[list[type[AnyMappingModel]]] = list(
    get_args(AnyMappingModel)
)
MAPPING_MODEL_CLASSES_BY_NAME: Final[dict[str, type[AnyMappingModel]]] = {
    cls.__name__: cls for cls in MAPPING_MODEL_CLASSES
}
# MAPPING_MODEL_BY_EXTRACTED_CLASS_NAME is deprecated, use MAPPING_MODEL_CLASSES_BY_NAME
MAPPING_MODEL_BY_EXTRACTED_CLASS_NAME = {
    f"Extracted{cls.stemType}": cls for cls in MAPPING_MODEL_CLASSES
}

AnyFilterModel = (
    AccessPlatformFilter
    | ActivityFilter
    | BibliographicResourceFilter
    | ConsentFilter
    | ContactPointFilter
    | DistributionFilter
    | OrganizationFilter
    | OrganizationalUnitFilter
    | PersonFilter
    | PrimarySourceFilter
    | ResourceFilter
    | VariableFilter
    | VariableGroupFilter
)
FilterModelTypeAdapter: TypeAdapter[AnyFilterModel] = TypeAdapter(
    Annotated[AnyFilterModel, Field(discriminator="entityType")]
)
FILTER_MODEL_CLASSES: Final[list[type[AnyFilterModel]]] = list(get_args(AnyFilterModel))
FILTER_MODEL_CLASSES_BY_NAME: Final[dict[str, type[AnyFilterModel]]] = {
    cls.__name__: cls for cls in FILTER_MODEL_CLASSES
}
# FILTER_MODEL_BY_EXTRACTED_CLASS_NAME is deprecated, use FILTER_MODEL_CLASSES_BY_NAME
FILTER_MODEL_BY_EXTRACTED_CLASS_NAME = {
    f"Extracted{cls.stemType}": cls for cls in FILTER_MODEL_CLASSES
}
