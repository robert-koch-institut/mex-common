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
            json_schema=core_schema.no_info_after_validator_function(
                cls, core_schema.str_schema(pattern=VOCABULARY_PATTERN)
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


class Country(VocabularyEnum):
    """The type of a country."""

    __scheme__ = "https://mex.rki.de/item/country"

    ARUBA = "https://mex.rki.de/item/country-1"
    AFGHANISTAN = "https://mex.rki.de/item/country-2"
    ANGOLA = "https://mex.rki.de/item/country-3"
    ANGUILLA = "https://mex.rki.de/item/country-4"
    LAND_ISLANDS = "https://mex.rki.de/item/country-5"
    ALBANIA = "https://mex.rki.de/item/country-6"
    ANDORRA = "https://mex.rki.de/item/country-7"
    UNITED_ARAB_EMIRATES = "https://mex.rki.de/item/country-8"
    ARGENTINA = "https://mex.rki.de/item/country-9"
    ARMENIA = "https://mex.rki.de/item/country-10"
    AMERICAN_SAMOA = "https://mex.rki.de/item/country-11"
    ANTARCTICA = "https://mex.rki.de/item/country-12"
    ANTIGUA_AND_BARBUDA = "https://mex.rki.de/item/country-13"
    AUSTRALIA = "https://mex.rki.de/item/country-14"
    AUSTRIA = "https://mex.rki.de/item/country-15"
    AZERBAIJAN = "https://mex.rki.de/item/country-16"
    BURUNDI = "https://mex.rki.de/item/country-17"
    BELGIUM = "https://mex.rki.de/item/country-18"
    BENIN = "https://mex.rki.de/item/country-19"
    BONAIRE_SINT_EUSTATIUS_AND_SABA = "https://mex.rki.de/item/country-20"
    BURKINA_FASO = "https://mex.rki.de/item/country-21"
    BANGLADESH = "https://mex.rki.de/item/country-22"
    BULGARIA = "https://mex.rki.de/item/country-23"
    BAHRAIN = "https://mex.rki.de/item/country-24"
    THE_BAHAMAS = "https://mex.rki.de/item/country-25"
    BOSNIA_AND_HERZEGOVINA = "https://mex.rki.de/item/country-26"
    SAINT_BARTH_LEMY = "https://mex.rki.de/item/country-27"
    BELARUS = "https://mex.rki.de/item/country-28"
    BELIZE = "https://mex.rki.de/item/country-29"
    BERMUDA = "https://mex.rki.de/item/country-30"
    BOLIVIA = "https://mex.rki.de/item/country-31"
    BRAZIL = "https://mex.rki.de/item/country-32"
    BARBADOS = "https://mex.rki.de/item/country-33"
    BRUNEI = "https://mex.rki.de/item/country-34"
    BHUTAN = "https://mex.rki.de/item/country-35"
    BOUVET_ISLAND = "https://mex.rki.de/item/country-36"
    BOTSWANA = "https://mex.rki.de/item/country-37"
    CENTRAL_AFRICAN_REPUBLIC = "https://mex.rki.de/item/country-38"
    CANADA = "https://mex.rki.de/item/country-39"
    COCOS_KEELING_ISLANDS = "https://mex.rki.de/item/country-40"
    SWITZERLAND = "https://mex.rki.de/item/country-41"
    CHILE = "https://mex.rki.de/item/country-42"
    CHINA = "https://mex.rki.de/item/country-43"
    C_TE_D_IVOIRE = "https://mex.rki.de/item/country-44"
    CAMEROON = "https://mex.rki.de/item/country-45"
    DEMOCRATIC_REPUBLIC_OF_THE_CONGO = "https://mex.rki.de/item/country-46"
    CONGO = "https://mex.rki.de/item/country-47"
    COOK_ISLANDS = "https://mex.rki.de/item/country-48"
    COLOMBIA = "https://mex.rki.de/item/country-49"
    COMOROS = "https://mex.rki.de/item/country-50"
    CLIPPERTON = "https://mex.rki.de/item/country-51"
    CABO_VERDE = "https://mex.rki.de/item/country-52"
    COSTA_RICA = "https://mex.rki.de/item/country-53"
    SARK = "https://mex.rki.de/item/country-54"
    CUBA = "https://mex.rki.de/item/country-55"
    CURA_AO = "https://mex.rki.de/item/country-56"
    CHRISTMAS_ISLAND = "https://mex.rki.de/item/country-57"
    CAYMAN_ISLANDS = "https://mex.rki.de/item/country-58"
    CYPRUS = "https://mex.rki.de/item/country-59"
    CZECH_REPUBLIC = "https://mex.rki.de/item/country-60"
    GERMANY = "https://mex.rki.de/item/country-61"
    DJIBOUTI = "https://mex.rki.de/item/country-62"
    DOMINICA = "https://mex.rki.de/item/country-63"
    DENMARK = "https://mex.rki.de/item/country-64"
    DOMINICAN_REPUBLIC = "https://mex.rki.de/item/country-65"
    ALGERIA = "https://mex.rki.de/item/country-66"
    ECUADOR = "https://mex.rki.de/item/country-67"
    EGYPT = "https://mex.rki.de/item/country-68"
    ERITREA = "https://mex.rki.de/item/country-69"
    WESTERN_SAHARA = "https://mex.rki.de/item/country-70"
    SPAIN = "https://mex.rki.de/item/country-71"
    ESTONIA = "https://mex.rki.de/item/country-72"
    ETHIOPIA = "https://mex.rki.de/item/country-73"
    EUROPEAN_UNION = "https://mex.rki.de/item/country-74"
    FINLAND = "https://mex.rki.de/item/country-75"
    FIJI = "https://mex.rki.de/item/country-76"
    FALKLAND_ISLANDS = "https://mex.rki.de/item/country-77"
    FRANCE = "https://mex.rki.de/item/country-78"
    FAROES = "https://mex.rki.de/item/country-79"
    MICRONESIA = "https://mex.rki.de/item/country-80"
    GABON = "https://mex.rki.de/item/country-81"
    UNITED_KINGDOM = "https://mex.rki.de/item/country-82"
    GEORGIA = "https://mex.rki.de/item/country-83"
    GUERNSEY = "https://mex.rki.de/item/country-84"
    GHANA = "https://mex.rki.de/item/country-85"
    GIBRALTAR = "https://mex.rki.de/item/country-86"
    GUINEA = "https://mex.rki.de/item/country-87"
    GUADELOUPE = "https://mex.rki.de/item/country-88"
    THE_GAMBIA = "https://mex.rki.de/item/country-89"
    GUINEA_BISSAU = "https://mex.rki.de/item/country-90"
    EQUATORIAL_GUINEA = "https://mex.rki.de/item/country-91"
    GREECE = "https://mex.rki.de/item/country-92"
    GRENADA = "https://mex.rki.de/item/country-93"
    GREENLAND = "https://mex.rki.de/item/country-94"
    GUATEMALA = "https://mex.rki.de/item/country-95"
    FRENCH_GUIANA = "https://mex.rki.de/item/country-96"
    GUAM = "https://mex.rki.de/item/country-97"
    GUYANA = "https://mex.rki.de/item/country-98"
    HONG_KONG = "https://mex.rki.de/item/country-99"
    HEARD_ISLAND_AND_MCDONALD_ISLANDS = "https://mex.rki.de/item/country-100"
    HONDURAS = "https://mex.rki.de/item/country-101"
    CROATIA = "https://mex.rki.de/item/country-102"
    HAITI = "https://mex.rki.de/item/country-103"
    HUNGARY = "https://mex.rki.de/item/country-104"
    INDONESIA = "https://mex.rki.de/item/country-105"
    ISLE_OF_MAN = "https://mex.rki.de/item/country-106"
    INDIA = "https://mex.rki.de/item/country-107"
    BRITISH_INDIAN_OCEAN_TERRITORY = "https://mex.rki.de/item/country-108"
    IRELAND = "https://mex.rki.de/item/country-109"
    IRAN = "https://mex.rki.de/item/country-110"
    IRAQ = "https://mex.rki.de/item/country-111"
    ICELAND = "https://mex.rki.de/item/country-112"
    ISRAEL = "https://mex.rki.de/item/country-113"
    ITALY = "https://mex.rki.de/item/country-114"
    JAMAICA = "https://mex.rki.de/item/country-115"
    JERSEY = "https://mex.rki.de/item/country-116"
    JORDAN = "https://mex.rki.de/item/country-117"
    JAPAN = "https://mex.rki.de/item/country-118"
    KAZAKHSTAN = "https://mex.rki.de/item/country-119"
    KENYA = "https://mex.rki.de/item/country-120"
    KYRGYZSTAN = "https://mex.rki.de/item/country-121"
    CAMBODIA = "https://mex.rki.de/item/country-122"
    KIRIBATI = "https://mex.rki.de/item/country-123"
    SAINT_KITTS_AND_NEVIS = "https://mex.rki.de/item/country-124"
    SOUTH_KOREA = "https://mex.rki.de/item/country-125"
    KUWAIT = "https://mex.rki.de/item/country-126"
    LAOS = "https://mex.rki.de/item/country-127"
    LEBANON = "https://mex.rki.de/item/country-128"
    LIBERIA = "https://mex.rki.de/item/country-129"
    LIBYA = "https://mex.rki.de/item/country-130"
    SAINT_LUCIA = "https://mex.rki.de/item/country-131"
    LIECHTENSTEIN = "https://mex.rki.de/item/country-132"
    SRI_LANKA = "https://mex.rki.de/item/country-133"
    LESOTHO = "https://mex.rki.de/item/country-134"
    LITHUANIA = "https://mex.rki.de/item/country-135"
    LUXEMBOURG = "https://mex.rki.de/item/country-136"
    LATVIA = "https://mex.rki.de/item/country-137"
    MACAO = "https://mex.rki.de/item/country-138"
    SAINT_MARTIN = "https://mex.rki.de/item/country-139"
    MOROCCO = "https://mex.rki.de/item/country-140"
    MONACO = "https://mex.rki.de/item/country-141"
    MOLDOVA = "https://mex.rki.de/item/country-142"
    MADAGASCAR = "https://mex.rki.de/item/country-143"
    MALDIVES = "https://mex.rki.de/item/country-144"
    MEXICO = "https://mex.rki.de/item/country-145"
    MARSHALL_ISLANDS = "https://mex.rki.de/item/country-146"
    NORTH_MACEDONIA = "https://mex.rki.de/item/country-147"
    MALI = "https://mex.rki.de/item/country-148"
    MALTA = "https://mex.rki.de/item/country-149"
    MONTENEGRO = "https://mex.rki.de/item/country-150"
    MONGOLIA = "https://mex.rki.de/item/country-151"
    NORTHERN_MARIANA_ISLANDS = "https://mex.rki.de/item/country-152"
    MOZAMBIQUE = "https://mex.rki.de/item/country-153"
    MAURITANIA = "https://mex.rki.de/item/country-154"
    MONTSERRAT = "https://mex.rki.de/item/country-155"
    MARTINIQUE = "https://mex.rki.de/item/country-156"
    MAURITIUS = "https://mex.rki.de/item/country-157"
    MALAWI = "https://mex.rki.de/item/country-158"
    MALAYSIA = "https://mex.rki.de/item/country-159"
    MAYOTTE = "https://mex.rki.de/item/country-160"
    NAMIBIA = "https://mex.rki.de/item/country-161"
    NEW_CALEDONIA = "https://mex.rki.de/item/country-162"
    NIGER = "https://mex.rki.de/item/country-163"
    NORFOLK_ISLAND = "https://mex.rki.de/item/country-164"
    NIGERIA = "https://mex.rki.de/item/country-165"
    NICARAGUA = "https://mex.rki.de/item/country-166"
    NIUE = "https://mex.rki.de/item/country-167"
    NETHERLANDS = "https://mex.rki.de/item/country-168"
    NORWAY = "https://mex.rki.de/item/country-169"
    NEPAL = "https://mex.rki.de/item/country-170"
    NAURU = "https://mex.rki.de/item/country-171"
    NEW_ZEALAND = "https://mex.rki.de/item/country-172"
    OMAN = "https://mex.rki.de/item/country-173"
    PAKISTAN = "https://mex.rki.de/item/country-174"
    PANAMA = "https://mex.rki.de/item/country-175"
    PITCAIRN_ISLANDS = "https://mex.rki.de/item/country-176"
    PERU = "https://mex.rki.de/item/country-177"
    PHILIPPINES = "https://mex.rki.de/item/country-178"
    PALAU = "https://mex.rki.de/item/country-179"
    PAPUA_NEW_GUINEA = "https://mex.rki.de/item/country-180"
    POLAND = "https://mex.rki.de/item/country-181"
    PUERTO_RICO = "https://mex.rki.de/item/country-182"
    NORTH_KOREA = "https://mex.rki.de/item/country-183"
    PORTUGAL = "https://mex.rki.de/item/country-184"
    PARAGUAY = "https://mex.rki.de/item/country-185"
    PALESTINE = "https://mex.rki.de/item/country-186"
    FRENCH_POLYNESIA = "https://mex.rki.de/item/country-187"
    QATAR = "https://mex.rki.de/item/country-188"
    R_UNION = "https://mex.rki.de/item/country-189"
    ROMANIA = "https://mex.rki.de/item/country-190"
    RUSSIA = "https://mex.rki.de/item/country-191"
    RWANDA = "https://mex.rki.de/item/country-192"
    SAUDI_ARABIA = "https://mex.rki.de/item/country-193"
    SUDAN = "https://mex.rki.de/item/country-194"
    SENEGAL = "https://mex.rki.de/item/country-195"
    SINGAPORE = "https://mex.rki.de/item/country-196"
    SOUTH_GEORGIA_AND_THE_SOUTH_SANDWICH_ISLANDS = "https://mex.rki.de/item/country-197"
    SAINT_HELENA_ASCENSION_AND_TRISTAN_DA_CUNHA = "https://mex.rki.de/item/country-198"
    SVALBARD_AND_JAN_MAYEN = "https://mex.rki.de/item/country-199"
    SOLOMON_ISLANDS = "https://mex.rki.de/item/country-200"
    SIERRA_LEONE = "https://mex.rki.de/item/country-201"
    EL_SALVADOR = "https://mex.rki.de/item/country-202"
    SAN_MARINO = "https://mex.rki.de/item/country-203"
    SOMALIA = "https://mex.rki.de/item/country-204"
    SAINT_PIERRE_AND_MIQUELON = "https://mex.rki.de/item/country-205"
    SERBIA = "https://mex.rki.de/item/country-206"
    SOUTH_SUDAN = "https://mex.rki.de/item/country-207"
    S_O_TOM_AND_PR_NCIPE = "https://mex.rki.de/item/country-208"
    SURINAME = "https://mex.rki.de/item/country-209"
    SLOVAKIA = "https://mex.rki.de/item/country-210"
    SLOVENIA = "https://mex.rki.de/item/country-211"
    SWEDEN = "https://mex.rki.de/item/country-212"
    ESWATINI = "https://mex.rki.de/item/country-213"
    SINT_MAARTEN = "https://mex.rki.de/item/country-214"
    SEYCHELLES = "https://mex.rki.de/item/country-215"
    SYRIA = "https://mex.rki.de/item/country-216"
    TURKS_AND_CAICOS_ISLANDS = "https://mex.rki.de/item/country-217"
    CHAD = "https://mex.rki.de/item/country-218"
    TOGO = "https://mex.rki.de/item/country-219"
    THAILAND = "https://mex.rki.de/item/country-220"
    TAJIKISTAN = "https://mex.rki.de/item/country-221"
    TOKELAU = "https://mex.rki.de/item/country-222"
    TURKMENISTAN = "https://mex.rki.de/item/country-223"
    TIMOR_LESTE = "https://mex.rki.de/item/country-224"
    TONGA = "https://mex.rki.de/item/country-225"
    TRINIDAD_AND_TOBAGO = "https://mex.rki.de/item/country-226"
    TUNISIA = "https://mex.rki.de/item/country-227"
    T_RKIYE = "https://mex.rki.de/item/country-228"
    TUVALU = "https://mex.rki.de/item/country-229"
    TAIWAN = "https://mex.rki.de/item/country-230"
    TANZANIA = "https://mex.rki.de/item/country-231"
    UGANDA = "https://mex.rki.de/item/country-232"
    UKRAINE = "https://mex.rki.de/item/country-233"
    URUGUAY = "https://mex.rki.de/item/country-234"
    UNITED_STATES_OF_AMERICA = "https://mex.rki.de/item/country-235"
    UZBEKISTAN = "https://mex.rki.de/item/country-236"
    HOLY_SEE = "https://mex.rki.de/item/country-237"
    SAINT_VINCENT_AND_THE_GRENADINES = "https://mex.rki.de/item/country-238"
    VENEZUELA = "https://mex.rki.de/item/country-239"
    BRITISH_VIRGIN_ISLANDS = "https://mex.rki.de/item/country-240"
    US_VIRGIN_ISLANDS = "https://mex.rki.de/item/country-241"
    VIET_NAM = "https://mex.rki.de/item/country-242"
    VANUATU = "https://mex.rki.de/item/country-243"
    WALLIS_AND_FUTUNA = "https://mex.rki.de/item/country-244"
    SAMOA = "https://mex.rki.de/item/country-245"
    ASHMORE_AND_CARTIER_ISLANDS = "https://mex.rki.de/item/country-246"
    B_SINGEN_AM_HOCHRHEIN = "https://mex.rki.de/item/country-247"
    CAMPIONE_D_ITALIA = "https://mex.rki.de/item/country-248"
    GAZA_STRIP = "https://mex.rki.de/item/country-249"
    CANARY_ISLANDS = "https://mex.rki.de/item/country-250"
    HELIGOLAND = "https://mex.rki.de/item/country-251"
    KOSOVO = "https://mex.rki.de/item/country-252"
    FEZZAN = "https://mex.rki.de/item/country-253"
    LIVIGNO = "https://mex.rki.de/item/country-254"
    MOUNT_ATHOS = "https://mex.rki.de/item/country-255"
    MELANESIA = "https://mex.rki.de/item/country-256"
    AZORES = "https://mex.rki.de/item/country-257"
    MADEIRA = "https://mex.rki.de/item/country-258"
    CEUTA = "https://mex.rki.de/item/country-259"
    SOMALILAND = "https://mex.rki.de/item/country-260"
    MELILLA = "https://mex.rki.de/item/country-261"
    PARACEL_ISLANDS = "https://mex.rki.de/item/country-262"
    SPRATLY_ISLANDS = "https://mex.rki.de/item/country-263"
    AKSAI_CHIN = "https://mex.rki.de/item/country-264"
    ARUNACHAL_PRADESH = "https://mex.rki.de/item/country-265"
    HALA_IB_TRIANGLE = "https://mex.rki.de/item/country-266"
    ILEMI_TRIANGLE = "https://mex.rki.de/item/country-267"
    JAMMU_AND_KASHMIR = "https://mex.rki.de/item/country-268"
    NORTHERN_IRELAND = "https://mex.rki.de/item/country-269"
    LIANCOURT_ROCKS = "https://mex.rki.de/item/country-270"
    NAVASSA_ISLAND = "https://mex.rki.de/item/country-271"
    SCARBOROUGH_REEF = "https://mex.rki.de/item/country-272"
    SENKAKU_ISLANDS = "https://mex.rki.de/item/country-273"
    CHAGOS_ISLANDS = "https://mex.rki.de/item/country-274"
    SAPODILLA_CAYES = "https://mex.rki.de/item/country-275"
    ABYEI_REGION = "https://mex.rki.de/item/country-276"
    BIR_TAWIL = "https://mex.rki.de/item/country-277"
    YEMEN = "https://mex.rki.de/item/country-278"
    SOUTH_AFRICA = "https://mex.rki.de/item/country-279"
    ZAMBIA = "https://mex.rki.de/item/country-280"
    ZIMBABWE = "https://mex.rki.de/item/country-281"


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
    THREE_TIMES_A_WEEK = "https://mex.rki.de/item/frequency-14"
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
