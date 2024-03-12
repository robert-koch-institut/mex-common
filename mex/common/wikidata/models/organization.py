from typing import Annotated, Optional, Union

from pydantic import ConfigDict, Field, model_validator

from mex.common.models import BaseModel


class Value(BaseModel):
    """Model class for Values (for claims)."""

    text: str | None = None
    language: str | None = None


class DataValue(BaseModel):
    """Model class for Data Values (for claims)."""

    value: Value

    @model_validator(mode="before")
    @classmethod
    def transform_strings_to_dict(
        cls, values: dict[str, Union[str, dict[str, str]]]
    ) -> Union[dict[str, dict[str, str | None]], dict[str, Union[str, dict[str, str]]]]:
        """Transform string and null value to a dict for parsing.

        Args:
            values: values that needs to be parsed

        Returns:
            resulting dict
        """
        value = values.get("value")
        if value is None or isinstance(value, str):
            return {"value": {"language": None, "text": value}}
        return values


class Mainsnak(BaseModel):
    """Model class for Mainsnack (for claims)."""

    datavalue: DataValue


class Claim(BaseModel):
    """Model class a Claim."""

    mainsnak: Mainsnak


class Claims(BaseModel):
    """model class for Claims."""

    website: Annotated[list[Claim], Field(alias="P856")] = []
    isni_id: Annotated[list[Claim], Field(alias="P213")] = []
    ror_id: Annotated[list[Claim], Field(alias="P6782")] = []
    official_name: Annotated[list[Claim], Field(alias="P1448")] = []
    short_name: Annotated[list[Claim], Field(alias="P1813")] = []
    native_label: Annotated[list[Claim], Field(alias="P1705")] = []
    gepris_id: Annotated[list[Claim], Field(alias="P4871")] = []
    gnd_id: Annotated[list[Claim], Field(alias="P227")] = []
    viaf_id: Annotated[list[Claim], Field(alias="P214")] = []


class Label(BaseModel):
    """Model class for single Label."""

    language: str
    value: str


class Labels(BaseModel):
    """Model class for Labels."""

    de: Optional[Label] = None
    en: Optional[Label] = None


class Alias(BaseModel):
    """Model class for single alias."""

    language: str
    value: str


class Aliases(BaseModel):
    """Model class for aliases."""

    de: list[Alias] = []
    en: list[Alias] = []


class WikidataOrganization(BaseModel):
    """Model class for Wikidata sources."""

    model_config = ConfigDict(extra="ignore")

    identifier: Annotated[str, Field(alias="id")]
    labels: Labels
    claims: Claims
    aliases: Aliases
