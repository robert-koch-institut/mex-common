from typing import TYPE_CHECKING, Annotated, Any

from pydantic import BaseModel, Field, create_model

from mex.common.transform import ensure_postfix

if TYPE_CHECKING:  # pragma: no cover
    from mex.common.models import AnyExtractedModel


class EntityFilterRule(BaseModel, extra="forbid"):
    """Entity filter rule model."""

    forValues: list[str] | None = None
    rule: str | None = None


class EntityFilter(BaseModel, extra="forbid"):
    """Entity filter model."""

    fieldInPrimarySource: str
    locationInPrimarySource: str | None = None
    examplesInPrimarySource: list[str] | None = None
    mappingRules: Annotated[list[EntityFilterRule], Field(min_length=1)]
    comment: str | None = None


def generate_entity_filter_schema(
    extracted_model: type["AnyExtractedModel"],
) -> type[BaseModel]:
    """Create a mapping schema for an entity filter for an extracted model class.

    Example entity filter: If activity starts before 2016: do not extract.

    Args:
        extracted_model: a pydantic model for an extracted model class

    Returns:
        model of the mapping schema for an entity filter
    """
    fields: dict[str, Any] = {
        extracted_model.__name__: (list[EntityFilter], None),
    }
    entity_filter_name = ensure_postfix(extracted_model.stemType, "EntityFilter")
    entity_filter_model: type[BaseModel] = create_model(
        entity_filter_name,
        **fields,
    )
    entity_filter_model.__doc__ = (
        f"Schema for entity filters for the entity type {extracted_model.__name__}."
    )
    return entity_filter_model
