"""A consent - for example, an interdepartmental project."""

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
    hasConsentType: ConsentType | None = None


class _RequiredValues(_Stem):
    hasConsentStatus: ConsentStatus
    hasDataSubject: MergedPersonIdentifier
    isIndicatedAtTime: YearMonthDayTime


class _SparseValues(_Stem):
    hasConsentStatus: ConsentStatus | None = None
    hasDataSubject: MergedPersonIdentifier | None = None
    isIndicatedAtTime: YearMonthDayTime | None = None


class _VariadicValues(_Stem):
    hasConsentType: list[ConsentType] = []
    hasConsentStatus: list[ConsentStatus] = []
    hasDataSubject: list[MergedPersonIdentifier] = []
    isIndicatedAtTime: list[YearMonthDayTime] = []


class BaseConsent(_OptionalValues, _RequiredValues):
    """All fields for a valid consent except for provenance."""


class ExtractedConsent(BaseConsent, ExtractedData):
    """An automatically extracted metadata set describing a consent."""

    entityType: Annotated[
        Literal["ExtractedConsent"], Field(alias="$type", frozen=True)
    ] = "ExtractedConsent"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(self) -> ExtractedConsentIdentifier:
        """Return the computed identifier for this extracted item."""
        return self._get_identifier(ExtractedConsentIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(self) -> MergedConsentIdentifier:  # noqa: N802
        """Return the computed stableTargetId for this extracted item."""
        return self._get_stable_target_id(MergedConsentIdentifier)


class MergedConsent(BaseConsent, MergedItem):
    """The result of merging all extracted items and rules for a consent."""

    entityType: Annotated[
        Literal["MergedConsent"], Field(alias="$type", frozen=True)
    ] = "MergedConsent"
    identifier: Annotated[MergedConsentIdentifier, Field(frozen=True)]


class PreviewConsent(_OptionalValues, _SparseValues, PreviewItem):
    """Preview for merging all extracted items and rules for a consent."""

    entityType: Annotated[
        Literal["PreviewConsent"], Field(alias="$type", frozen=True)
    ] = "PreviewConsent"
    identifier: Annotated[MergedConsentIdentifier, Field(frozen=True)]


class AdditiveConsent(_OptionalValues, _SparseValues, AdditiveRule):
    """Rule to add values to merged consent items."""

    entityType: Annotated[
        Literal["AdditiveConsent"], Field(alias="$type", frozen=True)
    ] = "AdditiveConsent"


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
    hadPrimarySource: Annotated[
        list[MappingField[MergedPrimarySourceIdentifier]], Field(min_length=1)
    ]
    identifierInPrimarySource: Annotated[list[MappingField[str]], Field(min_length=1)]
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
