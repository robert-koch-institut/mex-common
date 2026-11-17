from collections.abc import Iterable
from typing import (
    Annotated,
    Any,
    ClassVar,
    Generic,
    Protocol,
    TypeVar,
    get_args,
    overload,
)

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, GetCoreSchemaHandler
from pydantic_core import core_schema

from mex.common.models.base.model import BaseModel
from mex.common.types import MergedPrimarySourceIdentifier

_ValueT = TypeVar("_ValueT")
_ValueT_co = TypeVar("_ValueT_co", covariant=True)
_ItemT = TypeVar("_ItemT")


class _SupportsMappingValues(Protocol[_ValueT_co]):
    """Protocol for items that can resolve static values."""

    def get_static_values(self) -> _ValueT_co | None: ...


class _MappingListMixin:
    """Mixin for lists of mapping items with shared validation and helpers."""

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

    def get_static_values(
        self: Iterable[_SupportsMappingValues[_ValueT]],
    ) -> _ValueT | None:
        """Return the first static value of any of the items."""
        for item in self:
            static_values = item.get_static_values()
            if static_values is not None:
                return static_values
        return None


class MappingRule(PydanticBaseModel, Generic[_ValueT], extra="forbid"):
    """Generic mapping rule model."""

    forValues: Annotated[list[str] | None, Field(title="forValues")] = None
    setValues: Annotated[_ValueT | None, Field(title="setValues")] = None
    rule: Annotated[str | None, Field(title="rule")] = None

    def get_mapped_values(self, value_in_primary_source: str) -> _ValueT | None:
        """Return `setValues` if the value is listed in `forValues`."""
        if self.forValues and value_in_primary_source in self.forValues:
            return self.setValues
        return None

    def get_mappable_values(self) -> list[str]:
        """Return the `forValues` this rule can map."""
        return self.forValues or []

    def get_static_values(self) -> _ValueT | None:
        """Return `setValues` if the rule does not depend on `forValues`."""
        if not self.forValues:
            return self.setValues
        return None


class MappingRuleList(_MappingListMixin, list[MappingRule[_ValueT]]):
    """List of mapping rules with helpers to resolve mapped values."""

    _item_type = MappingRule

    @overload
    def get_mapped_values(
        self: "MappingRuleList[list[_ItemT]]", value_in_primary_source: str
    ) -> list[_ItemT]: ...

    @overload
    def get_mapped_values(
        self: "MappingRuleList[_ItemT]", value_in_primary_source: str
    ) -> list[_ItemT]: ...

    def get_mapped_values(self, value_in_primary_source: str) -> list[Any]:
        """Return the flattened values mapped by all of the mapping rules."""
        mapped_values: list[Any] = []
        for rule in self:
            set_values = rule.get_mapped_values(value_in_primary_source)
            if isinstance(set_values, list):
                mapped_values.extend(set_values)
            elif set_values is not None:
                mapped_values.append(set_values)
        return mapped_values

    def get_mappable_values(self) -> list[str]:
        """Return the flattened values all of the mapping rules can map."""
        return [
            mappable_value
            for rule in self
            for mappable_value in rule.get_mappable_values()
        ]


class MappingField(PydanticBaseModel, Generic[_ValueT], extra="forbid"):
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

    def _matches_source(
        self,
        field_in_primary_source: str | None,
        location_in_primary_source: str | None,
    ) -> bool:
        """Check whether the field matches the given field and location filters."""
        return (
            field_in_primary_source is None
            or field_in_primary_source == self.fieldInPrimarySource
        ) and (
            location_in_primary_source is None
            or location_in_primary_source == self.locationInPrimarySource
        )

    @overload
    def get_mapped_values(
        self: "MappingField[list[_ItemT]]",
        value_in_primary_source: str,
        field_in_primary_source: str | None = None,
        location_in_primary_source: str | None = None,
    ) -> list[_ItemT]: ...

    @overload
    def get_mapped_values(
        self: "MappingField[_ItemT]",
        value_in_primary_source: str,
        field_in_primary_source: str | None = None,
        location_in_primary_source: str | None = None,
    ) -> list[_ItemT]: ...

    def get_mapped_values(
        self,
        value_in_primary_source: str,
        field_in_primary_source: str | None = None,
        location_in_primary_source: str | None = None,
    ) -> list[Any]:
        """Return the flattened values mapped by all of the mapping rules.

        Args:
            value_in_primary_source: Value to look up in the `forValues` of the rules
            field_in_primary_source: Only match if equal to `fieldInPrimarySource`
            location_in_primary_source: Only match if equal to
                `locationInPrimarySource`

        Returns:
            Flattened list of `setValues` of all matching rules
        """
        if not self._matches_source(
            field_in_primary_source, location_in_primary_source
        ):
            return []
        return self.mappingRules.get_mapped_values(value_in_primary_source)

    def get_mappable_values(
        self,
        field_in_primary_source: str | None = None,
        location_in_primary_source: str | None = None,
    ) -> list[str]:
        """Return the flattened values all of the mapping rules can map.

        Args:
            field_in_primary_source: Only match if equal to `fieldInPrimarySource`
            location_in_primary_source: Only match if equal to
                `locationInPrimarySource`

        Returns:
            Flattened list of `forValues` of all rules
        """
        if not self._matches_source(
            field_in_primary_source, location_in_primary_source
        ):
            return []
        return self.mappingRules.get_mappable_values()

    def get_static_values(self) -> _ValueT | None:
        """Return the first static value of any of the mapping rules."""
        return self.mappingRules.get_static_values()


class MappingFieldList(_MappingListMixin, list[MappingField[_ValueT]]):
    """List of mapping fields with helpers to resolve mapped values."""

    _item_type = MappingField

    @overload
    def get_mapped_values(
        self: "MappingFieldList[list[_ItemT]]",
        value_in_primary_source: str,
        field_in_primary_source: str | None = None,
        location_in_primary_source: str | None = None,
    ) -> list[_ItemT]: ...

    @overload
    def get_mapped_values(
        self: "MappingFieldList[_ItemT]",
        value_in_primary_source: str,
        field_in_primary_source: str | None = None,
        location_in_primary_source: str | None = None,
    ) -> list[_ItemT]: ...

    def get_mapped_values(
        self,
        value_in_primary_source: str,
        field_in_primary_source: str | None = None,
        location_in_primary_source: str | None = None,
    ) -> list[Any]:
        """Return the flattened values mapped by all of the mapping fields.

        Args:
            value_in_primary_source: Value to look up in the `forValues` of the rules
            field_in_primary_source: Only match fields with this `fieldInPrimarySource`
            location_in_primary_source: Only match fields with this
                `locationInPrimarySource`

        Returns:
            Flattened list of `setValues` of all matching rules of all matching fields
        """
        return [
            mapped_values
            for field in self
            for mapped_values in field.get_mapped_values(
                value_in_primary_source,
                field_in_primary_source,
                location_in_primary_source,
            )
        ]

    def get_mappable_values(
        self,
        field_in_primary_source: str | None = None,
        location_in_primary_source: str | None = None,
    ) -> list[str]:
        """Return the flattened values all of the mapping fields can map.

        Args:
            field_in_primary_source: Only match fields with this `fieldInPrimarySource`
            location_in_primary_source: Only match fields with this
                `locationInPrimarySource`

        Returns:
            Flattened list of `forValues` of all rules of all matching fields
        """
        return [
            mappable_value
            for field in self
            for mappable_value in field.get_mappable_values(
                field_in_primary_source, location_in_primary_source
            )
        ]


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
