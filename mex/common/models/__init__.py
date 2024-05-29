"""These models implement the types defined by the `mex-model` in their various stages.

The current set of entity types includes:

- AccessPlatform
- Activity
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

- `ExtractedTEntityFilter` defines how an entity filter specification should look like
- `ExtractedTMapping` defines how a raw data to extracted item mapping should look like

Since these models for different use cases have a lot of overlapping attributes,
we use a number of intermediate private classes to compose the public classes:

- `_OptionalLists` defines all fields typed as lists with an arity of 0-n
- `_RequiredLists` defines all fields typed as lists with an arity of 1-n
- `_SparseLists` re-defines all fields from `_RequiredLists` with an arity of 0-n

- `_OptionalValues` defines all fields with optional values (arity of 0-1)
- `_RequiredValues` defines all fields with required values (arity of 1)
- `_SparseValues` re-defines all fields from `_RequiredValues` with an arity of 0-1
- `_VariadicValues` re-defines all fields from `_OptionalValues` and `_RequiredValues`
  as list fields with an arity of 0-n

These private classes are used to compose the public classes like so:

- BaseT: _OptionalLists, _RequiredLists, _OptionalValues, _RequiredValues
- ExtractedT: BaseT, ExtractedData
- MergedT: BaseT, MergedItem

- AdditiveT: _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, AdditiveRule
- SubtractiveT: _OptionalLists, _SparseLists, _VariadicValues, SubtractiveRule
- PreventiveT: all fields from BaseT re-typed as MergedPrimarySourceIdentifier

- ExtractedTEntityFilter: all BaseT fields re-typed as a list of EntityFilter
- ExtractedTMapping: all BaseT fields re-typed as lists of subclasses of GenericField

In addition to the classes themselves, `mex.common.models` also exposes various
lists of models, lookups by class name and typing for unions of models.
"""

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
from mex.common.models.filter import generate_entity_filter_schema
from mex.common.models.mapping import generate_mapping_schema_for_mex_class
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
    "FILTER_MODEL_BY_EXTRACTED_CLASS_NAME",
    "MAPPING_MODEL_BY_EXTRACTED_CLASS_NAME",
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

FILTER_MODEL_BY_EXTRACTED_CLASS_NAME = {
    cls.__name__: generate_entity_filter_schema(mex_model_class=cls)
    for cls in EXTRACTED_MODEL_CLASSES
}

MAPPING_MODEL_BY_EXTRACTED_CLASS_NAME = {
    cls.__name__: generate_mapping_schema_for_mex_class(mex_model_class=cls)
    for cls in EXTRACTED_MODEL_CLASSES
}
