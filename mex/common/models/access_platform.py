from typing import Annotated, ClassVar, Literal

from pydantic import AfterValidator, Field, computed_field

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
    APIType,
    ExtractedAccessPlatformIdentifier,
    Identifier,
    Link,
    MergedAccessPlatformIdentifier,
    MergedContactPointIdentifier,
    MergedOrganizationalUnitIdentifier,
    MergedPersonIdentifier,
    MergedPrimarySourceIdentifier,
    TechnicalAccessibility,
    Text,
)

AnyContactIdentifier = Annotated[
    MergedOrganizationalUnitIdentifier
    | MergedPersonIdentifier
    | MergedContactPointIdentifier,
    AfterValidator(Identifier),
]


class _Stem(BaseModel):
    stemType: ClassVar[Annotated[Literal["AccessPlatform"], Field(frozen=True)]] = (
        "AccessPlatform"
    )


class _OptionalLists(_Stem):
    alternativeTitle: Annotated[
        list[Text],
        Field(
            description="An alternative name for the access platform.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/alternative"]},
        ),
    ] = []
    contact: Annotated[
        list[AnyContactIdentifier],
        Field(
            description="An agent that serves as a contact for the access platform.",
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/dcat#contactPoint"]},
        ),
    ] = []
    description: Annotated[
        list[Text],
        Field(
            description="A short description of the access platform.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/description"]},
        ),
    ] = []
    landingPage: Annotated[
        list[Link],
        Field(
            description=(
                "A Web page that can be navigated to in a Web browser to gain "
                "access to the catalog, a dataset, its distributions and/or "
                "additional information."
            ),
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/dcat#landingPage"]},
        ),
    ] = []
    title: Annotated[
        list[Text],
        Field(
            description="The name of the access platform.",
            json_schema_extra={"sameAs": ["http://purl.org/dc/terms/title"]},
        ),
    ] = []
    unitInCharge: Annotated[
        list[MergedOrganizationalUnitIdentifier],
        Field(
            description=(
                "This property refers to agents who assume responsibility and "
                "accountability for the resource and its appropriate maintenance."
            ),
            json_schema_extra={"sameAs": ["http://dcat-ap.de/def/dcatde/maintainer"]},
        ),
    ] = []


class _OptionalValues(_Stem):
    endpointDescription: Annotated[
        Link | None,
        Field(
            description=(
                "A description of the services available via the end-points, "
                "including their operations, parameters etc."
            ),
            json_schema_extra={
                "sameAs": ["http://www.w3.org/ns/dcat#endpointDescription"]
            },
        ),
    ] = None
    endpointType: Annotated[
        APIType | None,
        Field(
            description="The type of endpoint, e.g. REST.",
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/type"]},
        ),
    ] = None
    endpointURL: Annotated[
        Link | None,
        Field(
            description=(
                "The root location or primary endpoint of the service "
                "(a Web-resolvable IRI)"
            ),
            json_schema_extra={"sameAs": ["http://www.w3.org/ns/dcat#endpointURL"]},
        ),
    ] = None


class _RequiredValues(_Stem):
    technicalAccessibility: Annotated[
        TechnicalAccessibility,
        Field(
            description=(
                "Indicates form if the platform can be accessed only within RKI "
                "network (internally) or if the platform is accessible publicly "
                "(externally)."
            ),
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/type"]},
        ),
    ]


class _SparseValues(_Stem):
    technicalAccessibility: Annotated[
        TechnicalAccessibility | None,
        Field(
            description=(
                "Indicates form if the platform can be accessed only within RKI "
                "network (internally) or if the platform is accessible publicly "
                "(externally)."
            ),
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/type"]},
        ),
    ] = None


class _VariadicValues(_Stem):
    endpointDescription: Annotated[
        list[Link],
        Field(
            description=(
                "A description of the services available via the end-points, "
                "including their operations, parameters etc."
            ),
        ),
    ] = []
    endpointType: Annotated[
        list[APIType],
        Field(
            description="The type of endpoint, e.g. REST.",
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/type"]},
        ),
    ] = []
    endpointURL: Annotated[
        list[Link],
        Field(
            description=(
                "The root location or primary endpoint of the service "
                "(a Web-resolvable IRI)"
            ),
        ),
    ] = []
    technicalAccessibility: Annotated[
        list[TechnicalAccessibility],
        Field(
            description=(
                "Indicates form if the platform can be accessed only within RKI "
                "network (internally) or if the platform is accessible publicly "
                "(externally)."
            ),
            json_schema_extra={"subPropertyOf": ["http://purl.org/dc/terms/type"]},
        ),
    ] = []


class BaseAccessPlatform(
    _OptionalLists,
    _OptionalValues,
    _RequiredValues,
    json_schema_extra={
        "description": (
            "A technical system or service that provides access to distributions or "
            "resources."
        ),
        "sameAs": ["http://www.w3.org/ns/dcat#DataService"],
    },
):
    """All fields for a valid access platform except for provenance."""


class ExtractedAccessPlatform(BaseAccessPlatform, ExtractedData):
    """An automatically extracted metadata item describing an access platform."""

    entityType: Annotated[
        Literal["ExtractedAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "ExtractedAccessPlatform"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def identifier(  # noqa: D102
        self,
    ) -> Annotated[
        ExtractedAccessPlatformIdentifier,
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
        return self._get_identifier(ExtractedAccessPlatformIdentifier)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def stableTargetId(  # noqa: D102, N802
        self,
    ) -> Annotated[
        MergedAccessPlatformIdentifier,
        Field(
            description=(
                "The identifier of the merged item that this extracted item belongs to."
            )
        ),
    ]:
        return self._get_stable_target_id(MergedAccessPlatformIdentifier)


class MergedAccessPlatform(BaseAccessPlatform, MergedItem):
    """The result of merging all extracted items and rules for an access platform."""

    entityType: Annotated[
        Literal["MergedAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "MergedAccessPlatform"
    identifier: Annotated[
        MergedAccessPlatformIdentifier,
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
        MergedAccessPlatformIdentifier | None,
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


class PreviewAccessPlatform(
    _OptionalLists, _OptionalValues, _SparseValues, PreviewItem
):
    """Preview for merging all extracted items and rules for an access platform."""

    entityType: Annotated[
        Literal["PreviewAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "PreviewAccessPlatform"
    identifier: Annotated[
        MergedAccessPlatformIdentifier,
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
        MergedAccessPlatformIdentifier | None,
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


class AdditiveAccessPlatform(
    _OptionalLists, _OptionalValues, _SparseValues, AdditiveRule
):
    """Rule to add values to merged access platform items."""

    entityType: Annotated[
        Literal["AdditiveAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "AdditiveAccessPlatform"
    supersededBy: Annotated[
        MergedAccessPlatformIdentifier | None,
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


class SubtractiveAccessPlatform(_OptionalLists, _VariadicValues, SubtractiveRule):
    """Rule to subtract values from merged access platform items."""

    entityType: Annotated[
        Literal["SubtractiveAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "SubtractiveAccessPlatform"


class PreventiveAccessPlatform(_Stem, PreventiveRule):
    """Rule to prevent primary sources for fields of merged access platform items."""

    entityType: Annotated[
        Literal["PreventiveAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "PreventiveAccessPlatform"
    alternativeTitle: list[MergedPrimarySourceIdentifier] = []
    contact: list[MergedPrimarySourceIdentifier] = []
    description: list[MergedPrimarySourceIdentifier] = []
    endpointDescription: list[MergedPrimarySourceIdentifier] = []
    endpointType: list[MergedPrimarySourceIdentifier] = []
    endpointURL: list[MergedPrimarySourceIdentifier] = []
    landingPage: list[MergedPrimarySourceIdentifier] = []
    technicalAccessibility: list[MergedPrimarySourceIdentifier] = []
    title: list[MergedPrimarySourceIdentifier] = []
    unitInCharge: list[MergedPrimarySourceIdentifier] = []


class _BaseRuleSet(_Stem, RuleSet):
    """Base class for sets of rules for an access platform item."""

    additive: AdditiveAccessPlatform = AdditiveAccessPlatform()
    subtractive: SubtractiveAccessPlatform = SubtractiveAccessPlatform()
    preventive: PreventiveAccessPlatform = PreventiveAccessPlatform()


class AccessPlatformRuleSetRequest(_BaseRuleSet):
    """Set of rules to create or update an access platform item."""

    entityType: Annotated[
        Literal["AccessPlatformRuleSetRequest"], Field(alias="$type", frozen=True)
    ] = "AccessPlatformRuleSetRequest"


class AccessPlatformRuleSetResponse(_BaseRuleSet):
    """Set of rules to retrieve an access platform item."""

    entityType: Annotated[
        Literal["AccessPlatformRuleSetResponse"], Field(alias="$type", frozen=True)
    ] = "AccessPlatformRuleSetResponse"
    stableTargetId: MergedAccessPlatformIdentifier


class AccessPlatformMapping(_Stem, BaseMapping):
    """Mapping for describing an access platform transformation."""

    entityType: Annotated[
        Literal["AccessPlatformMapping"], Field(alias="$type", frozen=True)
    ] = "AccessPlatformMapping"
    technicalAccessibility: Annotated[
        list[MappingField[TechnicalAccessibility]], Field(min_length=1)
    ]
    endpointDescription: list[MappingField[Link | None]] = []
    endpointType: list[MappingField[APIType | None]] = []
    endpointURL: list[MappingField[Link | None]] = []
    alternativeTitle: list[MappingField[list[Text]]] = []
    contact: list[MappingField[list[AnyContactIdentifier]]] = []
    description: list[MappingField[list[Text]]] = []
    landingPage: list[MappingField[list[Link]]] = []
    title: list[MappingField[list[Text]]] = []
    unitInCharge: list[MappingField[list[MergedOrganizationalUnitIdentifier]]] = []


class AccessPlatformFilter(_Stem, BaseFilter):
    """Class for defining filter rules for access platform items."""

    entityType: Annotated[
        Literal["AccessPlatformFilter"], Field(alias="$type", frozen=True)
    ] = "AccessPlatformFilter"
    fields: Annotated[list[FilterField], Field(title="fields")] = []
