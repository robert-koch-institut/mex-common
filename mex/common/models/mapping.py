from typing import Annotated, Any, Optional, get_origin

from pydantic import BaseModel, Field, create_model

from mex.common.models import EXTRACTED_MODEL_CLASSES, ExtractedData


class GenericRule(BaseModel, extra="forbid"):
    """Generic mapping rule model."""

    forValues: list[str] | None = None
    setValues: list[Any] | None = None
    rule: str | None = None


class GenericField(BaseModel, extra="forbid"):
    """Generic Field model."""

    fieldInPrimarySource: str
    locationInPrimarySource: str | None = None
    examplesInPrimarySource: list[str] | None = None
    mappingRules: Annotated[list[GenericRule], Field(min_length=1)]
    comment: str | None = None


def generate_mapping_schema_for_mex_class(
    mex_model_class: type[ExtractedData],
) -> type[BaseModel]:
    """Create a mapping schema the MEx extracted model class.

    Pydantic models are dynamically created for the given entity type from
    depending on the respective fields and their types.

    Args:
        mex_model_class: a pydantic model (type) of a MEx model class/entity

    Returns:
        dynamic mapping model for the provided extracted model class
    """
    # dicts for create_model() must be declared as dict[str, Any] to silence mypy
    field_models: dict[str, Any] = {}
    for field_name, field_info in mex_model_class.model_fields.items():
        if field_name == "entityType":
            continue
        # first create dynamic rule model
        if get_origin(field_info.annotation) is list:
            rule_type: Any = field_info.annotation
        else:
            rule_type = list[field_info.annotation]  # type: ignore[name-defined]

        rule_model: type[GenericRule] = create_model(
            f"{field_name.capitalize()}MappingRule",
            __base__=(GenericRule,),
            setValues=(
                Optional[rule_type],
                None,
            ),
        )
        rule_model.__doc__ = str(
            f"Mapping rule schema of field {field_name.capitalize()}."
        )
        # then update the mappingRules type in the field in primary source schema
        field_model: type[GenericField] = create_model(
            f"{field_name.capitalize()}FieldsInPrimarySource",
            __base__=(GenericField,),
            mappingRules=(list[rule_model], Field(..., min_length=1)),  # type: ignore[valid-type]
        )
        field_model.__doc__ = str(
            f"Mapping schema for {field_name.capitalize()} fields in primary source."
        )
        if field_info.is_required():
            field_models[field_name] = (list[field_model], ...)  # type: ignore[valid-type]
        else:
            field_models[field_name] = (list[field_model], None)  # type: ignore[valid-type]
    mapping_name = f"{mex_model_class.__name__}Mapping".removeprefix("Extracted")
    class_model: type[BaseModel] = create_model(mapping_name, **field_models)
    name = mex_model_class.__name__
    class_model.__doc__ = str(
        f"Schema for mapping the properties of the entity type {name}."
    )
    return class_model


MAPPING_MODEL_BY_EXTRACTED_CLASS_NAME = {
    cls.__name__: generate_mapping_schema_for_mex_class(
        mex_model_class=cls,
    )
    for cls in EXTRACTED_MODEL_CLASSES
}
