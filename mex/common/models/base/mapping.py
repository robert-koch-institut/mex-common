from typing import Annotated, Any, Generic, TypeVar, get_args

from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import core_schema

from mex.common.types import MergedPrimarySourceIdentifier

_ValueT = TypeVar("_ValueT")


class MappingRule(BaseModel, Generic[_ValueT], extra="forbid"):
    """Generic mapping rule model."""

    forValues: Annotated[list[str] | None, Field(title="forValues")] = None
    setValues: Annotated[_ValueT | None, Field(title="setValues")] = None
    rule: Annotated[str | None, Field(title="rule")] = None

    def get_mapped_values(self, input_value: str) -> _ValueT | None:
        """Return `setValues` if the input value is listed in `forValues`."""
        if self.forValues and input_value in self.forValues:
            return self.setValues
        return None

    def get_static_values(self) -> _ValueT | None:
        """Return `setValues` if the rule does not depend on `forValues`."""
        if not self.forValues:
            return self.setValues
        return None


class MappingField(BaseModel, Generic[_ValueT], extra="forbid"):
    """Generic mapping field model."""

    fieldInPrimarySource: Annotated[
        str | None,
        Field(title="fieldInPrimarySource"),
    ] = None
    locationInPrimarySource: Annotated[
        str | None, Field(title="locationInPrimarySource")
    ] = None
    examplesInPrimarySource: Annotated[
        list[str] | None, Field(title="examplesInPrimarySource")
    ] = None
    mappingRules: Annotated[
        list[MappingRule[_ValueT]], Field(min_length=1, title="mappingRules")
    ]
    comment: Annotated[str | None, Field(title="comment")] = None

    def get_mapped_values(self, input_value: str) -> _ValueT | None:
        """Return the first value mapped by any of the mapping rules."""
        for rule in self.mappingRules:
            mapped_values = rule.get_mapped_values(input_value)
            if mapped_values is not None:
                return mapped_values
        return None

    def get_static_values(self) -> _ValueT | None:
        """Return the first static value of any of the mapping rules."""
        for rule in self.mappingRules:
            static_values = rule.get_static_values()
            if static_values is not None:
                return static_values
        return None


class MappingList(list[MappingField[_ValueT]], Generic[_ValueT]):
    """List of mapping fields with a helper to resolve a mapped value."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: object, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Validate as a list of mapping fields and wrap the result."""
        (value_type,) = get_args(source_type) or (Any,)
        return core_schema.no_info_after_validator_function(
            cls,
            handler.generate_schema(list[MappingField[value_type]]),  # type: ignore[valid-type]
        )

    def get_mapped_values(self, input_value: str) -> _ValueT | None:
        """Return the first value mapped by any of the mapping fields."""
        for field in self:
            mapped_values = field.get_mapped_values(input_value)
            if mapped_values is not None:
                return mapped_values
        return None

    def get_static_values(self) -> _ValueT | None:
        """Return the first static value of any of the mapping fields."""
        for field in self:
            static_values = field.get_static_values()
            if static_values is not None:
                return static_values
        return None


class BaseMapping(BaseModel, extra="forbid"):
    """Base class for mapping implementations."""

    hadPrimarySource: Annotated[
        MappingList[MergedPrimarySourceIdentifier],
        Field(min_length=1),
    ]
    identifierInPrimarySource: Annotated[
        MappingList[str],
        Field(min_length=1),
    ]
