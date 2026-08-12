from enum import Enum
from typing import ClassVar

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, json_schema
from pydantic_core import core_schema

VOCABULARY_PATTERN = r"https://mex.rki.de/item/[a-z0-9-]+"


class VocabularyEnum(Enum):
    """Base class for enums of concepts from a controlled vocabulary."""

    __scheme__: ClassVar[str]

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: object, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Modify the core schema to add the vocabulary regex."""
        return core_schema.json_or_python_schema(
            json_schema=core_schema.union_schema(
                [
                    core_schema.str_schema(pattern=VOCABULARY_PATTERN),
                    core_schema.no_info_plain_validator_function(cls),
                ],
            ),
            python_schema=core_schema.no_info_plain_validator_function(cls),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda s: s.value, when_used="unless-none"
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema_: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> json_schema.JsonSchemaValue:
        """Modify the json schema to add the scheme and an example."""
        json_schema_ = handler(core_schema_)
        json_schema_["examples"] = [str(next(iter(cls)).value)]
        json_schema_["useScheme"] = cls.__scheme__
        return json_schema_


class AccessRestriction(VocabularyEnum):
    """The access restriction type."""

    __scheme__ = "https://mex.rki.de/item/access-restriction"

    OPEN = "https://mex.rki.de/item/access-restriction-1"
    RESTRICTED = "https://mex.rki.de/item/access-restriction-2"


class ActivityType(VocabularyEnum):
    """The activity type."""

    __scheme__ = "https://mex.rki.de/item/activity-type"

    THIRD_PARTY_FUNDED_PROJECT = "https://mex.rki.de/item/activity-type-1"
    INTERNAL_PROJECT_ENDEAVOR = "https://mex.rki.de/item/activity-type-3"
    OTHER = "https://mex.rki.de/item/activity-type-6"


class AnonymizationPseudonymization(VocabularyEnum):
    """Whether the resource is anonymized/pseudonymized."""

    __scheme__ = "https://mex.rki.de/item/anonymization-pseudonymization"

    ANONYMIZED = "https://mex.rki.de/item/anonymization-pseudonymization-1"
    PSEUDONYMIZED = "https://mex.rki.de/item/anonymization-pseudonymization-2"


class APIType(VocabularyEnum):
    """Technical standard or style of a network API."""

    __scheme__ = "https://mex.rki.de/item/api-type"

    REST = "https://mex.rki.de/item/api-type-1"
    SOAP = "https://mex.rki.de/item/api-type-2"
    SPARQL_ENDPOINT = "https://mex.rki.de/item/api-type-3"
    PROPRIETARY = "https://mex.rki.de/item/api-type-4"
    RPC = "https://mex.rki.de/item/api-type-5"
    GRAPHQL = "https://mex.rki.de/item/api-type-6"
    OTHER = "https://mex.rki.de/item/api-type-7"


class BibliographicResourceType(VocabularyEnum):
    """The type of a bibliographic resource."""

    __scheme__ = "https://mex.rki.de/item/bibliographic-resource-type"

    BOOK = "https://mex.rki.de/item/bibliographic-resource-type-1"
    BOOK_CHAPTER = "https://mex.rki.de/item/bibliographic-resource-type-2"
    CONFERENCE_PAPER = "https://mex.rki.de/item/bibliographic-resource-type-3"
    DOCTORAL_THESIS = "https://mex.rki.de/item/bibliographic-resource-type-4"
    HABILITATION_THESIS = "https://mex.rki.de/item/bibliographic-resource-type-5"
    JOURNAL = "https://mex.rki.de/item/bibliographic-resource-type-6"
    JOURNAL_ARTICLE = "https://mex.rki.de/item/bibliographic-resource-type-7"
    OTHER = "https://mex.rki.de/item/bibliographic-resource-type-8"
    POSTER = "https://mex.rki.de/item/bibliographic-resource-type-9"
    PREPRINT = "https://mex.rki.de/item/bibliographic-resource-type-10"
    PRESENTATION = "https://mex.rki.de/item/bibliographic-resource-type-11"
    REPORT = "https://mex.rki.de/item/bibliographic-resource-type-12"
    SEMINAR_PAPER = "https://mex.rki.de/item/bibliographic-resource-type-13"
    THESIS = "https://mex.rki.de/item/bibliographic-resource-type-14"


class CodingSystem(VocabularyEnum):
    """The type of a coding system."""

    __scheme__ = "https://mex.rki.de/item/coding-system"

    ICD_10 = "https://mex.rki.de/item/coding-system-1"
    ICD_11 = "https://mex.rki.de/item/coding-system-2"
    LOINC = "https://mex.rki.de/item/coding-system-3"
    SNOMED_CLINICAL_TERMS = "https://mex.rki.de/item/coding-system-4"
    EDQM_STANDARD_TERMS = "https://mex.rki.de/item/coding-system-5"
    ICHI = "https://mex.rki.de/item/coding-system-6"
    MEDDRA = "https://mex.rki.de/item/coding-system-7"
    ORPHACODE = "https://mex.rki.de/item/coding-system-8"
    GMDN = "https://mex.rki.de/item/coding-system-9"
    HGNC = "https://mex.rki.de/item/coding-system-10"
    OPS = "https://mex.rki.de/item/coding-system-11"
    UCUM = "https://mex.rki.de/item/coding-system-12"
    RXNORM = "https://mex.rki.de/item/coding-system-13"
    ATC = "https://mex.rki.de/item/coding-system-14"
    UMLS = "https://mex.rki.de/item/coding-system-15"
    ICD_9_CM = "https://mex.rki.de/item/coding-system-16"
    ICD_O_3 = "https://mex.rki.de/item/coding-system-17"
    ICF = "https://mex.rki.de/item/coding-system-18"
    ICPC_3 = "https://mex.rki.de/item/coding-system-19"
    ICPC_2 = "https://mex.rki.de/item/coding-system-20"
    MESH = "https://mex.rki.de/item/coding-system-21"
    OTHER = "https://mex.rki.de/item/coding-system-22"


class ConsentStatus(VocabularyEnum):
    """The status of a consent."""

    __scheme__ = "https://mex.rki.de/item/consent-status"

    INVALID_FOR_PROCESSING = "https://mex.rki.de/item/consent-status-1"
    VALID_FOR_PROCESSING = "https://mex.rki.de/item/consent-status-2"


class ConsentType(VocabularyEnum):
    """The type of a consent."""

    __scheme__ = "https://mex.rki.de/item/consent-type"

    EXPRESSED_CONSENT = "https://mex.rki.de/item/consent-type-2"


class DataProcessingState(VocabularyEnum):
    """Type for state of data processing."""

    __scheme__ = "https://mex.rki.de/item/data-processing-state"

    RAW_DATA = "https://mex.rki.de/item/data-processing-state-1"
    SECONDARY_DATA = "https://mex.rki.de/item/data-processing-state-2"
    AGGREGATED = "https://mex.rki.de/item/data-processing-state-3"
    PLAUSIBILITY_CHECKED = "https://mex.rki.de/item/data-processing-state-4"
    NORMALIZED = "https://mex.rki.de/item/data-processing-state-5"


class Frequency(VocabularyEnum):
    """Frequency type."""

    __scheme__ = "https://mex.rki.de/item/frequency"

    TRIENNIAL = "https://mex.rki.de/item/frequency-1"
    BIENNIAL = "https://mex.rki.de/item/frequency-2"
    ANNUAL = "https://mex.rki.de/item/frequency-3"
    SEMIANNUAL = "https://mex.rki.de/item/frequency-4"
    THREE_TIMES_A_YEAR = "https://mex.rki.de/item/frequency-5"
    QUARTERLY = "https://mex.rki.de/item/frequency-6"
    BIMONTHLY = "https://mex.rki.de/item/frequency-7"
    MONTHLY = "https://mex.rki.de/item/frequency-8"
    SEMIMONTHLY = "https://mex.rki.de/item/frequency-9"
    BIWEEKLY = "https://mex.rki.de/item/frequency-10"
    THREE_TIMES_A_MONTH = "https://mex.rki.de/item/frequency-11"
    WEEKLY = "https://mex.rki.de/item/frequency-12"
    SEMIWEEKLY = "https://mex.rki.de/item/frequency-13"
    THREE_TIME_A_WEEK = "https://mex.rki.de/item/frequency-14"
    DAILY = "https://mex.rki.de/item/frequency-15"
    CONTINUOUS = "https://mex.rki.de/item/frequency-16"
    IRREGULAR = "https://mex.rki.de/item/frequency-17"


class HealthCategory(VocabularyEnum):
    """Type for health category."""

    __scheme__ = "https://mex.rki.de/item/health-category"

    ELECTRONIC_HEALTH_DATA_FROM_EHRS = "https://mex.rki.de/item/health-category-1"
    MEDICAL_AND_MORTALITY_REGISTRY_DATA = "https://mex.rki.de/item/health-category-2"
    OTHER_HUMAN_MOLECULAR_AND_OMICS_DATA = "https://mex.rki.de/item/health-category-3"
    DATA_ON_HEALTH_PROFESSIONALS = "https://mex.rki.de/item/health-category-4"
    MEDICINAL_AND_MEDICAL_PRODUCT_REGISTRY_DATA = (
        "https://mex.rki.de/item/health-category-5"
    )
    DATA_ON_HEALTH_DETERMINANTS = "https://mex.rki.de/item/health-category-6"
    DATA_FROM_RESEARCH_COHORTS_AND_SURVEYS = "https://mex.rki.de/item/health-category-7"
    OTHER_DATA_FROM_MEDICAL_DEVICES = "https://mex.rki.de/item/health-category-8"
    DATA_FROM_REGULATED_CLINICAL_RESEARCH = "https://mex.rki.de/item/health-category-9"
    AGGREGATED_DATA_ON_HEALTHCARE_NEEDS_PROVISION_AND_RESOURCES = (
        "https://mex.rki.de/item/health-category-10"
    )
    AUTOMATICALLY_GENERATED_PERSONAL_ELECTRONIC_HEALTH_DATA = (
        "https://mex.rki.de/item/health-category-11"
    )
    HUMAN_GENETIC_EPIGENOMIC_AND_GENOMIC_DATA = (
        "https://mex.rki.de/item/health-category-12"
    )
    ADMINISTRATIVE_DATA = "https://mex.rki.de/item/health-category-13"
    DATA_ON_PATHOGENS = "https://mex.rki.de/item/health-category-14"
    HEALTH_DATA_FROM_BIOBANKS = "https://mex.rki.de/item/health-category-15"
    DATA_FROM_POPULATION_BASED_HEALTH_DATA_REGISTRIES = (
        "https://mex.rki.de/item/health-category-16"
    )
    WELLNESS_APPLICATION_DATA = "https://mex.rki.de/item/health-category-17"


class Language(VocabularyEnum):
    """Language type."""

    __scheme__ = "https://mex.rki.de/item/language"

    GERMAN = "https://mex.rki.de/item/language-1"
    ENGLISH = "https://mex.rki.de/item/language-2"
    FRENCH = "https://mex.rki.de/item/language-3"
    SPANISH = "https://mex.rki.de/item/language-4"
    RUSSIAN = "https://mex.rki.de/item/language-5"


class License(VocabularyEnum):
    """License type."""

    __scheme__ = "https://mex.rki.de/item/license"

    CREATIVE_COMMONS_ATTRIBUTION_4_0_INTERNATIONAL = "https://mex.rki.de/item/license-1"


class MIMEType(VocabularyEnum):
    """The mime type."""

    __scheme__ = "https://mex.rki.de/item/mime-type"

    DOCX = "https://mex.rki.de/item/mime-type-1"
    XLSX = "https://mex.rki.de/item/mime-type-2"
    PPTX = "https://mex.rki.de/item/mime-type-3"
    PDF = "https://mex.rki.de/item/mime-type-4"
    TIFF = "https://mex.rki.de/item/mime-type-5"
    MHTML = "https://mex.rki.de/item/mime-type-6"
    CSV = "https://mex.rki.de/item/mime-type-7"
    XML = "https://mex.rki.de/item/mime-type-8"
    ATOM = "https://mex.rki.de/item/mime-type-9"
    SAS = "https://mex.rki.de/item/mime-type-10"
    STATA = "https://mex.rki.de/item/mime-type-11"
    FASTQ = "https://mex.rki.de/item/mime-type-12"
    TSV = "https://mex.rki.de/item/mime-type-13"
    PPT = "https://mex.rki.de/item/mime-type-14"
    XLS = "https://mex.rki.de/item/mime-type-15"
    ZIP = "https://mex.rki.de/item/mime-type-16"
    TAR_GZ = "https://mex.rki.de/item/mime-type-17"
    HTML = "https://mex.rki.de/item/mime-type-18"
    JSON = "https://mex.rki.de/item/mime-type-19"


class PersonalData(VocabularyEnum):
    """Classification of personal data."""

    __scheme__ = "https://mex.rki.de/item/personal-data"

    PERSONAL_DATA = "https://mex.rki.de/item/personal-data-1"
    NO_PERSONAL_DATA = "https://mex.rki.de/item/personal-data-2"


class Purpose(VocabularyEnum):
    """The purpose of processing data."""

    __scheme__ = "https://mex.rki.de/item/purpose"

    MONITORING_SURVEILLANCE = "https://mex.rki.de/item/purpose-1"
    IDENTIFYING_TRENDS = "https://mex.rki.de/item/purpose-11"
    DETECTION_OF_UNUSUAL_EVENTS_AND_EARLY_WARNING = "https://mex.rki.de/item/purpose-12"
    ESTIMATING_THE_BURDEN_OF_DISEASE = "https://mex.rki.de/item/purpose-13"
    INFORMATION_REPORTING = "https://mex.rki.de/item/purpose-2"
    INFORMATION_FOR_THE_PROFESSIONAL_COMMUNITY = "https://mex.rki.de/item/purpose-21"
    INFORMATION_FOR_DECISION_MAKERS = "https://mex.rki.de/item/purpose-22"
    INFORMATION_FOR_THE_PUBLIC = "https://mex.rki.de/item/purpose-23"
    MEASURES_QUALITY_CONTROL = "https://mex.rki.de/item/purpose-3"
    DERIVING_RECOMMENDATIONS_FOR_PREVENTIVE_MEASURES = (
        "https://mex.rki.de/item/purpose-31"
    )
    EVALUATION_OF_MEASURES = "https://mex.rki.de/item/purpose-32"
    HEALTHCARE_GOVERNANCE = "https://mex.rki.de/item/purpose-33"
    RESEARCH = "https://mex.rki.de/item/purpose-4"
    PATHOGEN_DIAGNOSIS = "https://mex.rki.de/item/purpose-5"
    OTHER = "https://mex.rki.de/item/purpose-6"


class ResourceCreationMethod(VocabularyEnum):
    """The creation method of a resource."""

    __scheme__ = "https://mex.rki.de/item/resource-creation-method"

    OTHER = "https://mex.rki.de/item/resource-creation-method-1"
    STUDIES_SURVEYS_AND_INTERVIEWS = (
        "https://mex.rki.de/item/resource-creation-method-2"
    )
    SURVEILLANCE = "https://mex.rki.de/item/resource-creation-method-3"
    LABORATORY_TESTS = "https://mex.rki.de/item/resource-creation-method-4"
    SEQUENCING = "https://mex.rki.de/item/resource-creation-method-5"
    REGISTRY = "https://mex.rki.de/item/resource-creation-method-6"
    MODELS_AND_SIMULATIONS = "https://mex.rki.de/item/resource-creation-method-7"


class ResourceTypeGeneral(VocabularyEnum):
    """The general type of a resource."""

    __scheme__ = "https://mex.rki.de/item/resource-type-general"

    SAMPLES = "https://mex.rki.de/item/resource-type-general-2"
    DATA_COLLECTION = "https://mex.rki.de/item/resource-type-general-13"
    DATASET = "https://mex.rki.de/item/resource-type-general-14"
    TEXT = "https://mex.rki.de/item/resource-type-general-15"
    IMAGE = "https://mex.rki.de/item/resource-type-general-16"
    SOFTWARE_CODE = "https://mex.rki.de/item/resource-type-general-17"
    OTHER = "https://mex.rki.de/item/resource-type-general-18"


class TechnicalAccessibility(VocabularyEnum):
    """Technical accessibility within RKI and outside of RKI."""

    __scheme__ = "https://mex.rki.de/item/technical-accessibility"

    INTERNAL = "https://mex.rki.de/item/technical-accessibility-1"
    EXTERNAL = "https://mex.rki.de/item/technical-accessibility-2"


class Theme(VocabularyEnum):
    """The theme type."""

    __scheme__ = "https://mex.rki.de/item/theme"

    PUBLIC_HEALTH = "https://mex.rki.de/item/theme-1"
    INFECTIOUS_DISEASES_AND_EPIDEMIOLOGY = "https://mex.rki.de/item/theme-11"
    PATHOGENESIS_RESEARCH_AND_DIAGNOSTIC_DEVELOPMENT = (
        "https://mex.rki.de/item/theme-20"
    )
    GENERAL_MICROBIOLOGY_AND_MOLECULAR_BIOLOGY = "https://mex.rki.de/item/theme-21"
    BIOLOGICAL_TOXIN_RESEARCH_AND_DIAGNOSTICS = "https://mex.rki.de/item/theme-22"
    BIOINFORMATICS_AND_SYSTEMS_BIOLOGY = "https://mex.rki.de/item/theme-23"
    ANIMAL_EXPERIMENTAL_RESEARCH_AND_3R = "https://mex.rki.de/item/theme-24"
    ARTIFICIAL_INTELLIGENCE_AND_MACHINE_LEARNING = "https://mex.rki.de/item/theme-25"
    NON_COMMUNICABLE_DISEASES_AND_HEALTH_SURVEILLANCE = (
        "https://mex.rki.de/item/theme-36"
    )
    INTERNATIONAL_HEALTH_PROTECTION = "https://mex.rki.de/item/theme-37"
