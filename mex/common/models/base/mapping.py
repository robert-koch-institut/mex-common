from collections.abc import Iterable
from typing import Annotated, Any, ClassVar, Generic, Protocol, TypeVar, get_args

from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import core_schema

from mex.common.types import MergedPrimarySourceIdentifier

_ValueT = TypeVar("_ValueT")
_ValueT_co = TypeVar("_ValueT_co", covariant=True)


class _SupportsMappingValues(Protocol[_ValueT_co]):
    """Protocol for items that can resolve mapped and static values."""

    def get_mapped_values(self, input_value: str) -> _ValueT_co | None: ...

    def get_static_values(self) -> _ValueT_co | None: ...


class _MappingListMixin:
    """Mixin for lists of mapping items that resolve the first non-null value."""

    _item_type: ClassVar[Any]

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: object, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Validate as a list of mapping items and wrap the result."""
        (value_type,) = get_args(source_type) or (Any,)
        return core_schema.no_info_after_validator_function(
            cls,
            handler.generate_schema(list[cls._item_type[value_type]]),  # type: ignore[name-defined]
        )

    def get_mapped_values(
        self: Iterable[_SupportsMappingValues[_ValueT]], input_value: str
    ) -> _ValueT | None:
        """Return the first value mapped by any of the items."""
        for item in self:
            mapped_values = item.get_mapped_values(input_value)
            if mapped_values is not None:
                return mapped_values
        return None

    def get_static_values(
        self: Iterable[_SupportsMappingValues[_ValueT]],
    ) -> _ValueT | None:
        """Return the first static value of any of the items."""
        for item in self:
            static_values = item.get_static_values()
            if static_values is not None:
                return static_values
        return None


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


class MappingRuleList(_MappingListMixin, list[MappingRule[_ValueT]]):
    """List of mapping rules with helpers to resolve mapped values."""

    _item_type = MappingRule


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
        MappingRuleList[_ValueT], Field(min_length=1, title="mappingRules")
    ]
    comment: Annotated[str | None, Field(title="comment")] = None

    def get_mapped_values(self, input_value: str) -> _ValueT | None:
        """Return the first value mapped by any of the mapping rules."""
        return self.mappingRules.get_mapped_values(input_value)

    def get_static_values(self) -> _ValueT | None:
        """Return the first static value of any of the mapping rules."""
        return self.mappingRules.get_static_values()


class MappingFieldList(_MappingListMixin, list[MappingField[_ValueT]]):
    """List of mapping fields with helpers to resolve mapped values."""

    _item_type = MappingField


class BaseMapping(BaseModel, extra="forbid"):
    """Base class for mapping implementations."""

    hadPrimarySource: Annotated[
        MappingFieldList[MergedPrimarySourceIdentifier],
        Field(min_length=1),
    ]
    identifierInPrimarySource: Annotated[
        MappingFieldList[str],
        Field(min_length=1),
    ]
