from typing import Annotated, ClassVar, Literal

from pydantic import Field, computed_field

from mex.common.models.base.extracted_data import ExtractedData
from mex.common.models.base.filter import BaseFilter, FilterField
from mex.common.models.base.mapping import BaseMapping, MappingField
from mex.common.models.base.merged_item import MergedItem
from mex.common.models.base.model import BaseModel
from mex.common.models.base.preview_item import PreviewItem
from mex.common.models.base.rules import (
    AdditiveRule,
    PreventiveRule,
    RuleSet,
    SubtractiveRule,
    WorkflowRule,
)
from mex.common.types import (
    ExtractedLocationIdentifier,
    MergedLocationIdentifier,
    MergedPrimarySourceIdentifier,
    Text,
)

GeoNamesIdStr = Annotated[
    str,
    Field(
        pattern="^http://www\\.geonames\\.org/[0-9]{7}$",
        json_schema_extra={"format": "uri"},
    ),
]
WikidataIdStr = Annotated[
    str,
    Field(
        pattern="^http://www\\.wikidata\\.org/entity/[PQ0-9]{2,64}$",
        examples=[
            "http://www.wikidata.org/entity/Q679041",
            "http://www.wikidata.org/entity/Q918501",
            "http://www.wikidata.org/entity/Q491566",
        ],
        json_schema_extra={"format": "uri"},
    ),
]


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["Location"], Field(frozen=True)]] = "Location"


class _OptionalLists(_Stem):
    geoNamesId: Annotated[
        list[GeoNamesIdStr],
        Field(
            description="Identifier in the GeoNames geographical database.",
            json_schema_extra={"closeMatch": ["http://www.wikidata.org/entity/P1566"]},
        ),
    ] = []
    wikidataId: Annotated[
        list[WikidataIdStr],
        Field(description="Identifier from Wikidata."),
    ] = []


class _RequiredLists(_Stem):
    name: Annotated[
        list[Text],
        Field(
            description="Name of the location.",
            min_length=1,
            json_schema_extra={"closeMatch": ["http://www.wikidata.org/name"]},
        ),
    ]


class _SparseLists(_Stem):
    name: Annotated[
        list[Text],
        Field(
            description="Name of the location.",
            json_schema_extra={"closeMatch": ["http://www.wikidata.org/name"]},
        ),
    ] = []


class BaseLocation(
    _OptionalLists,
    _RequiredLists,
    json_schema_extra={
        "description": "A spatial region or named place.",
    },
):
    """All fields for a valid location except for provenance."""


class ExtractedLocation(BaseLocation, ExtractedData):
    """An automatically extracted metadata set describing a location."""

    entityType: Annotated[
        Literal["ExtractedLocation"], Field(alias="$type", frozen=True)
    ] = "ExtractedLocation"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(  # noqa: D102
        self,
    ) -> Annotated[
        ExtractedLocationIdentifier,
        Field(
            description=(
                "An unambiguous reference to the resource within a given context. "
                "Persistent identifiers should be provided as HTTP URIs "
                "([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={
                "closeMatch": ["http://purl.org/dc/elements/1.1/identifier"]
            },
        ),
    ]:
        return self._get_identifier(ExtractedLocationIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(  # noqa: D102, N802
        self,
    ) -> Annotated[
        MergedLocationIdentifier,
        Field(
            description=(
                "The identifier of the merged item that this extracted item belongs to."
            )
        ),
    ]:
        return self._get_stable_target_id(MergedLocationIdentifier)


class MergedLocation(BaseLocation, MergedItem):
    """The result of merging all extracted items and rules for a location."""

    entityType: Annotated[
        Literal["MergedLocation"], Field(alias="$type", frozen=True)
    ] = "MergedLocation"
    identifier: Annotated[
        MergedLocationIdentifier,
        Field(
            json_schema_extra={
                "description": (
                    "An unambiguous reference to the resource within a given context. "
                    "Persistent identifiers should be provided as HTTP URIs "
                    "([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
                ),
                "readOnly": True,
                "closeMatch": ["http://purl.org/dc/elements/1.1/identifier"],
            },
            frozen=True,
        ),
    ]
    supersededBy: Annotated[
        MergedLocationIdentifier | None,
        Field(
            json_schema_extra={
                "description": (
                    "A merged item which is the preferred duplicate, because it "
                    "replaces, consolidates or otherwise makes the current merged item "
                    "obsolete."
                ),
            }
        ),
    ] = None


class PreviewLocation(_OptionalLists, _SparseLists, PreviewItem):
    """Preview for merging all extracted items and rules for a location."""

    entityType: Annotated[
        Literal["PreviewLocation"], Field(alias="$type", frozen=True)
    ] = "PreviewLocation"
    identifier: Annotated[
        MergedLocationIdentifier,
        Field(
            json_schema_extra={
                "description": (
                    "An unambiguous reference to the resource within a given context. "
                    "Persistent identifiers should be provided as HTTP URIs "
                    "([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
                ),
                "readOnly": True,
                "closeMatch": ["http://purl.org/dc/elements/1.1/identifier"],
            },
            frozen=True,
        ),
    ]
    supersededBy: Annotated[
        MergedLocationIdentifier | None,
        Field(
            json_schema_extra={
                "description": (
                    "A merged item which is the preferred duplicate, because it "
                    "replaces, consolidates or otherwise makes the current merged item "
                    "obsolete."
                ),
            }
        ),
    ] = None


class AdditiveLocation(_OptionalLists, _SparseLists, AdditiveRule):
    """Rule to add values to merged location items."""

    entityType: Annotated[
        Literal["AdditiveLocation"], Field(alias="$type", frozen=True)
    ] = "AdditiveLocation"
    supersededBy: Annotated[
        MergedLocationIdentifier | None,
        Field(
            json_schema_extra={
                "description": (
                    "A merged item which is the preferred duplicate, because it "
                    "replaces, consolidates or otherwise makes the current merged item "
                    "obsolete."
                ),
            }
        ),
    ] = None


class SubtractiveLocation(_OptionalLists, _SparseLists, SubtractiveRule):
    """Rule to subtract values from merged location items."""

    entityType: Annotated[
        Literal["SubtractiveLocation"], Field(alias="$type", frozen=True)
    ] = "SubtractiveLocation"


class PreventiveLocation(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged location items."""

    entityType: Annotated[
        Literal["PreventiveLocation"], Field(alias="$type", frozen=True)
    ] = "PreventiveLocation"
    geoNamesId: list[MergedPrimarySourceIdentifier] = []
    name: list[MergedPrimarySourceIdentifier] = []
    wikidataId: list[MergedPrimarySourceIdentifier] = []


class WorkflowLocation(_Stem, WorkflowRule):
    """Rule to prevent publishing of merged location items."""

    entityType: Annotated[
        Literal["WorkflowLocation"], Field(alias="$type", frozen=True)
    ] = "WorkflowLocation"


class _BaseRuleSet(_Stem, RuleSet):
    """Base class for sets of rules for a location item."""

    additive: AdditiveLocation = AdditiveLocation()
    subtractive: SubtractiveLocation = SubtractiveLocation()
    preventive: PreventiveLocation = PreventiveLocation()
    workflow: WorkflowLocation = WorkflowLocation()


class LocationRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update a location item."""

    entityType: Annotated[
        Literal["LocationRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "LocationRuleSetRequest"


class LocationRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve a location item."""

    entityType: Annotated[
        Literal["LocationRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "LocationRuleSetResponse"
    stableTargetId: MergedLocationIdentifier


class LocationMapping(_Stem, BaseMapping):
    """Mapping for describing a location transformation."""

    entityType: Annotated[
        Literal["LocationMapping"], Field(alias="$type", frozen=True)
    ] = "LocationMapping"
    name: Annotated[list[MappingField[list[Text]]], Field(min_length=1)]
    geoNamesId: list[MappingField[list[GeoNamesIdStr]]] = []
    wikidataId: list[MappingField[list[WikidataIdStr]]] = []


class LocationFilter(_Stem, BaseFilter):
    """Class for defining filter rules for location items."""

    entityType: Annotated[
        Literal["LocationFilter"], Field(alias="$type", frozen=True)
    ] = "LocationFilter"
    fields: Annotated[list[FilterField], Field(title="fields")] = []
