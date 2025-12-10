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
)
from mex.common.types import (
    ConsentStatus,
    ConsentType,
    ExtractedConsentIdentifier,
    MergedConsentIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
    YearMonthDayTime,
)


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["Consent"], Field(frozen=True)]] = "Consent"


class _OptionalValues(_Stem):
    hasConsentType: Annotated[
        ConsentType | None,
        Field(
            description="The type of consent.",
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/type"]},
        ),
    ] = None


class _RequiredValues(_Stem):
    hasConsentStatus: Annotated[
        ConsentStatus,
        Field(
            description="Specifies the state or status of consent.",
            json_schema_extra={"sameAs": ["https://w3id.org/dpv#hasConsentStatus"]},
        ),
    ]
    hasDataSubject: Annotated[
        MergedPersonIdentifier,
        Field(
            description="Indicates association with Data Subject.",
            json_schema_extra={"sameAs": ["https://w3id.org/dpv#hasDataSubject"]},
        ),
    ]
    isIndicatedAtTime: Annotated[
        YearMonthDayTime,
        Field(
            description=(
                "Specifies the temporal information for when the entity has "
                "indicated the specific context."
            ),
            json_schema_extra={"sameAs": ["https://w3id.org/dpv#isIndicatedAtTime"]},
        ),
    ]


class _SparseValues(_Stem):
    hasConsentStatus: Annotated[
        ConsentStatus | None,
        Field(
            description="Specifies the state or status of consent.",
            json_schema_extra={"sameAs": ["https://w3id.org/dpv#hasConsentStatus"]},
        ),
    ] = None
    hasDataSubject: Annotated[
        MergedPersonIdentifier | None,
        Field(
            description="Indicates association with Data Subject.",
            json_schema_extra={"sameAs": ["https://w3id.org/dpv#hasDataSubject"]},
        ),
    ] = None
    hasConsentType: Annotated[
        ConsentType | None,
        Field(
            description="The type of consent.",
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/type"]},
        ),
    ] = None
    isIndicatedAtTime: Annotated[
        YearMonthDayTime | None,
        Field(
            description=(
                "Specifies the temporal information for when the entity has "
                "indicated the specific context."
            ),
            json_schema_extra={"sameAs": ["https://w3id.org/dpv#isIndicatedAtTime"]},
        ),
    ] = None


class _VariadicValues(_Stem):
    hasConsentType: Annotated[
        list[ConsentType],
        Field(
            description="The type of consent.",
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/type"]},
        ),
    ] = []
    hasConsentStatus: Annotated[
        list[ConsentStatus],
        Field(
            description=(
                "In DPV there is no property for the type of consent. In DPV, the "
                "types are subclasses of dpv:Consent. In order to align with our "
                "modelling approach, we model types of consent as a concept "
                "(skos:Concept). Since dpv:Consent is also defined as a "
                "skos:Concept, this is no conflict, just another way of "
                "implementing it."
            ),
            json_schema_extra={"sameAs": ["https://w3id.org/dpv#hasConsentStatus"]},
        ),
    ] = []
    hasDataSubject: Annotated[
        list[MergedPersonIdentifier],
        Field(
            description="Indicates association with Data Subject.",
            json_schema_extra={"sameAs": ["https://w3id.org/dpv#hasDataSubject"]},
        ),
    ] = []
    isIndicatedAtTime: Annotated[
        list[YearMonthDayTime],
        Field(
            description=(
                "Specifies the temporal information for when the entity has "
                "indicated the specific context."
            ),
            json_schema_extra={"sameAs": ["https://w3id.org/dpv#isIndicatedAtTime"]},
        ),
    ] = []


class BaseConsent(
    _OptionalValues,
    _RequiredValues,
    json_schema_extra={
        "description": "Consent of the Data Subject for specified process or activity.",
        "sameAs": ["https://w3id.org/dpv#Consent"],
    },
):
    """All fields for a valid consent except for provenance."""


class ExtractedConsent(BaseConsent, ExtractedData):
    """An automatically extracted metadata set describing a consent."""

    entityType: Annotated[
        Literal["ExtractedConsent"], Field(alias="$type", frozen=True)
    ] = "ExtractedConsent"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(  # noqa: D102
        self,
    ) -> Annotated[
        ExtractedConsentIdentifier,
        Field(
            description=(
                "An unambiguous reference to the resource within a given context. "
                "Persistent identifiers should be provided as HTTP URIs "
                "([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
            ),
            json_schema_extra={
                "sameAs": ["http://purl.org/dc/elements/1.1/identifier"]
            },
        ),
    ]:
        return self._get_identifier(ExtractedConsentIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(  # noqa: D102, N802
        self,
    ) -> Annotated[
        MergedConsentIdentifier,
        Field(
            description=(
                "The identifier of the merged item that this extracted item belongs to."
            )
        ),
    ]:
        return self._get_stable_target_id(MergedConsentIdentifier)


class MergedConsent(BaseConsent, MergedItem):
    """The result of merging all extracted items and rules for a consent."""

    entityType: Annotated[
        Literal["MergedConsent"], Field(alias="$type", frozen=True)
    ] = "MergedConsent"
    identifier: Annotated[
        MergedConsentIdentifier,
        Field(
            json_schema_extra={
                "description": (
                    "An unambiguous reference to the resource within a given context. "
                    "Persistent identifiers should be provided as HTTP URIs "
                    "([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
                ),
                "readOnly": True,
                "sameAs": ["http://purl.org/dc/elements/1.1/identifier"],
            },
            frozen=True,
        ),
    ]
    supersededBy: Annotated[
        MergedConsentIdentifier | None,
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


class PreviewConsent(_OptionalValues, _SparseValues, PreviewItem):
    """Preview for merging all extracted items and rules for a consent."""

    entityType: Annotated[
        Literal["PreviewConsent"], Field(alias="$type", frozen=True)
    ] = "PreviewConsent"
    identifier: Annotated[
        MergedConsentIdentifier,
        Field(
            json_schema_extra={
                "description": (
                    "An unambiguous reference to the resource within a given context. "
                    "Persistent identifiers should be provided as HTTP URIs "
                    "([DCT, 2020-01-20](http://dublincore.org/specifications/dublin-core/dcmi-terms/2020-01-20/))."
                ),
                "readOnly": True,
                "sameAs": ["http://purl.org/dc/elements/1.1/identifier"],
            },
            frozen=True,
        ),
    ]
    supersededBy: Annotated[
        MergedConsentIdentifier | None,
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


class AdditiveConsent(_OptionalValues, _SparseValues, AdditiveRule):
    """Rule to add values to merged consent items."""

    entityType: Annotated[
        Literal["AdditiveConsent"], Field(alias="$type", frozen=True)
    ] = "AdditiveConsent"
    supersededBy: Annotated[
        MergedConsentIdentifier | None,
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


class SubtractiveConsent(_VariadicValues, SubtractiveRule):
    """Rule to subtract values from merged consent items."""

    entityType: Annotated[
        Literal["SubtractiveConsent"], Field(alias="$type", frozen=True)
    ] = "SubtractiveConsent"


class PreventiveConsent(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged consent items."""

    entityType: Annotated[
        Literal["PreventiveConsent"], Field(alias="$type", frozen=True)
    ] = "PreventiveConsent"
    hasConsentType: list[MergedPrimarySourceIdentifier] = []
    hasConsentStatus: list[MergedPrimarySourceIdentifier] = []
    hasDataSubject: list[MergedPrimarySourceIdentifier] = []
    isIndicatedAtTime: list[MergedPrimarySourceIdentifier] = []


class _BaseRuleSet(_Stem, RuleSet):
    """Base class for sets of rules for a consent item."""

    additive: AdditiveConsent = AdditiveConsent()
    subtractive: SubtractiveConsent = SubtractiveConsent()
    preventive: PreventiveConsent = PreventiveConsent()


class ConsentRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update a consent item."""

    entityType: Annotated[
        Literal["ConsentRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "ConsentRuleSetRequest"


class ConsentRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve a consent item."""

    entityType: Annotated[
        Literal["ConsentRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "ConsentRuleSetResponse"
    stableTargetId: MergedConsentIdentifier


class ConsentMapping(_Stem, BaseMapping):
    """Mapping for describing a consent transformation."""

    entityType: Annotated[
        Literal["ConsentMapping"], Field(alias="$type", frozen=True)
    ] = "ConsentMapping"
    hasConsentStatus: Annotated[list[MappingField[ConsentStatus]], Field(min_length=1)]
    hasDataSubject: Annotated[
        list[MappingField[MergedPersonIdentifier]], Field(min_length=1)
    ]
    isIndicatedAtTime: Annotated[
        list[MappingField[YearMonthDayTime]], Field(min_length=1)
    ]
    hasConsentType: list[MappingField[ConsentType | None]] = []


class ConsentFilter(_Stem, BaseFilter):
    """Class for defining filter rules for consent items."""

    entityType: Annotated[
        Literal["ConsentFilter"], Field(alias="$type", frozen=True)
    ] = "ConsentFilter"
    fields: Annotated[list[FilterField], Field(title="fields")] = []
