from typing import Annotated, Any

from pydantic import BaseModel, Field, create_model

from mex.common.models import EXTRACTED_MODEL_CLASSES


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
    mex_model_class: type[BaseModel],
) -> type[BaseModel]:
    """Create a mapping schema for an entity filter for a Mex model class.

    Example entity filter: If activity starts before 2016: do not extract.

    Args:
        mex_model_class: a pydantic model (type) of a MEx model class/entity.

    Returns:
        model of the mapping schema for an entity filter for a Mex model class.
    """
    filters: dict[str, Any] = {
        f"{mex_model_class.__name__}": (list[EntityFilter], None)
    }

    entity_filter_model: type[BaseModel] = create_model(
        f"{mex_model_class.__name__}",
        **filters,
    )
    return entity_filter_model


FILTER_MODEL_BY_EXTRACTED_CLASS_NAME = {
    cls.__name__: generate_entity_filter_schema(
        mex_model_class=cls,
    )
    for cls in EXTRACTED_MODEL_CLASSES
}
