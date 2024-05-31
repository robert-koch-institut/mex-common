from typing import TYPE_CHECKING, Annotated, Any, get_origin

from pydantic import BaseModel, Field, create_model

from mex.common.transform import ensure_postfix

if TYPE_CHECKING:  # pragma: no cover
    from mex.common.models import AnyExtractedModel


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


def generate_mapping_schema(
    extracted_model: type["AnyExtractedModel"],
) -> type[BaseModel]:
    """Create a mapping schema the MEx extracted model class.

    Pydantic models are dynamically created for the given entity type from
    depending on the respective fields and their types.

    Args:
        extracted_model: a pydantic model for an extracted model class

    Returns:
        dynamic mapping model for the provided extracted model class
    """
    # dicts for create_model() must be declared as dict[str, Any] to silence mypy
    fields: dict[str, Any] = {}
    for field_name, field_info in extracted_model.model_fields.items():
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
                rule_type | None,
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
            fields[field_name] = (list[field_model], ...)  # type: ignore[valid-type]
        else:
            fields[field_name] = (list[field_model], None)  # type: ignore[valid-type]
    mapping_name = ensure_postfix(extracted_model.stemType, "Mapping")
    mapping_model: type[BaseModel] = create_model(mapping_name, **fields)
    mapping_model.__doc__ = (
        "Schema for mapping the properties of the entity type "
        f"{extracted_model.__name__}."
    )
    return mapping_model
