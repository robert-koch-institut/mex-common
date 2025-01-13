from typing import TYPE_CHECKING, Annotated, Any, get_origin

from pydantic import BaseModel, Field, create_model

from mex.common.transform import ensure_postfix

if TYPE_CHECKING:  # pragma: no cover
    from mex.common.models import AnyExtractedModel


class BaseMappingRule(BaseModel, extra="forbid"):
    """Generic mapping rule model."""

    forValues: Annotated[list[str] | None, Field(title="forValues")] = None
    setValues: Annotated[list[Any] | None, Field(title="setValues")] = None
    rule: Annotated[str | None, Field(title="rule")] = None


class BaseMappingField(BaseModel, extra="forbid"):
    """Generic mapping field model."""

    fieldInPrimarySource: Annotated[str, Field(title="fieldInPrimarySource")]
    locationInPrimarySource: Annotated[
        str | None, Field(title="locationInPrimarySource")
    ] = None
    examplesInPrimarySource: Annotated[
        list[str] | None, Field(title="examplesInPrimarySource")
    ] = None
    mappingRules: Annotated[
        list[BaseMappingRule], Field(min_length=1, title="mappingRules")
    ]
    comment: Annotated[str | None, Field(title="comment")] = None


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

        field_class_name = field_name[0].upper() + field_name[1:]

        rule_model: type[BaseMappingRule] = create_model(
            f"{field_class_name}MappingRule",
            __base__=(BaseMappingRule,),
            setValues=(
                Annotated[rule_type | None, Field(title="setValues")],
                None,
            ),
        )
        rule_model.__doc__ = str(f"Mapping rule schema for field {field_name}.")
        # then update the mappingRules type in the field in primary source schema
        field_model: type[BaseMappingField] = create_model(
            f"{field_class_name}MappingField",
            __base__=(BaseMappingField,),
            mappingRules=(
                list[rule_model],  # type: ignore[valid-type]
                Field(..., min_length=1, title="mappingRules"),
            ),
        )
        field_model.__doc__ = str(
            f"Mapping schema for {field_name} fields in primary source."
        )
        if field_info.is_required():
            fields[field_name] = (
                Annotated[list[field_model], Field(title=field_name)],  # type: ignore[valid-type]
                ...,
            )
        else:
            fields[field_name] = (
                Annotated[list[field_model], Field(title=field_name)],  # type: ignore[valid-type]
                [],
            )
    mapping_name = ensure_postfix(extracted_model.stemType, "Mapping")
    mapping_model: type[BaseModel] = create_model(mapping_name, **fields)
    mapping_model.__doc__ = (
        "Schema for mapping the properties of the entity type "
        f"{extracted_model.__name__}."
    )
    return mapping_model


def _materialize_mapping_schemas() -> None:
    import json
    from pathlib import Path
    from subprocess import run

    from mex.common.models import MAPPING_MODEL_BY_EXTRACTED_CLASS_NAME

    out_dir = Path.cwd()

    for name, model in MAPPING_MODEL_BY_EXTRACTED_CLASS_NAME.items():
        with open(
            out_dir / f"{name}_MappingSchema.json",
            "w",
            encoding="utf-8",
        ) as fh:
            fh.write(
                json.dumps(
                    model.model_json_schema(),
                    ensure_ascii=False,
                    indent=4,
                )
                + "\n"
            )
        print("written", out_dir / f"{name}_MappingSchema.json")  # noqa: T201
        run(  # noqa: S603
            [  # noqa: S607
                "datamodel-codegen",
                "--input",
                out_dir / f"{name}_MappingSchema.json",
                "--input-file-type",
                "jsonschema",
                "--output",
                out_dir / f"{name}.py",
            ],
            check=False,
        )
        print("written", out_dir / f"{name}.py")  # noqa: T201

        break


if __name__ == "__main__":
    _materialize_mapping_schemas()
