from pathlib import Path
from typing import Any, Optional, Union, cast

import jsonref
import yaml

from mex.common.logging import echo
from mex.common.models import EXTRACTED_MODEL_CLASSES
from mex.common.settings import BaseSettings


def __create_template_from_schema(
    schema: dict[str, Any]
) -> Optional[Union[dict[str, Any], list[Any]]]:
    """Recursively generate a template from a json schema.

    At the lowest level null values are inserted.

    Args:
        schema: The json schema loaded as a dictionary, with resolved references.

    Returns:
        template of the JSON schema as a dict/list.
    """
    if "anyOf" in schema:
        first_option = schema["anyOf"][0]  # Consider only the first sub schema
        return __create_template_from_schema(first_option)

    if "allOf" in schema and len(schema["allOf"]) == 1:
        return __create_template_from_schema(schema["allOf"][0])

    if "type" not in schema:  # e.g. language or Text
        return None

    if schema["type"] == "object":
        if "properties" in schema:
            yaml_template = {}
            for prop_name, prop_schema in schema["properties"].items():
                yaml_template[prop_name] = __create_template_from_schema(prop_schema)
            return yaml_template
        raise NotImplementedError(
            "currently need anyOf or properties for object sub-schema."
        )

    if schema["type"] == "array":
        items_schema = schema.get("items", {})
        min_items = schema.get("minItems", 1)

        nested_template = __create_template_from_schema(items_schema)
        return [nested_template] * min_items
    return None


def add_default_values(yaml_template: dict[str, Any]) -> dict[str, Any]:
    """Add default values and remove unnecessary fields in the templates.

    Args:
        yaml_template: dictionary to be saved as a yaml file without default values.

    Returns:
        template for the mapping file with added default values.
    """
    for key, val in yaml_template.items():
        if key not in ["identifier", "hadPrimarySource", "stableTargetId"]:
            continue
        attribute_details = yaml_template[key][0]
        attribute_rule = attribute_details["mappingRules"][0]
        del attribute_details["locationInPrimarySource"]
        del attribute_details["examplesInPrimarySource"]
        del attribute_details["comment"]
        del attribute_rule["forValues"]
        del attribute_rule["setValues"]
        attribute_details["fieldInPrimarySource"] = "n/a"
        if key == "identifier":
            attribute_rule["rule"] = "Assign identifier."
        if key == "hadPrimarySource":
            attribute_rule["rule"] = (
                "Assign 'stable target id' of primary source with identifier '...' "
                "in /raw-data/primary-sources/primary-sources.json."
            )
        if key == "stableTargetId":
            attribute_rule["rule"] = "Assign 'stable target id' of merged item."
    return yaml_template


def generate_mapping_template_from_schema(
    schema_path: Path, template_path: Path, default_values: bool
) -> None:
    """Generate a yaml mapping template from a json schema.

    Include the relative path to the schema in the header.

    Args:
        schema_path: path to json mapping of mapping file of an entity type.
        template_path: path where to save respective template file.
        default_values: if True, add default values for some fields.
    """
    with open(schema_path, "r") as schema_file:
        json_schema = jsonref.load(schema_file)  # replaces all references

    yaml_template = cast(dict[str, Any], __create_template_from_schema(json_schema))

    if default_values:
        yaml_template = add_default_values(yaml_template)

    header = f"""# yaml-language-server:
                $schema=../../__schema__/{schema_path.name}\n"""  # relative path
    yaml_output = f"""{header}\n
                {yaml.dump(yaml_template, default_flow_style=False, sort_keys=False)}
                """
    template_path.parent.mkdir(exist_ok=True, parents=True)
    with open(template_path, "w") as yaml_file:
        yaml_file.write(yaml_output)


def run_template_generation(
    entity_filters: bool = False, default_values: bool = True
) -> None:
    """Run template generation for all mex-model mappings or all entity filters.

    Settings:
        assets_dir: resolved path to the assets directory

    Args:
        entity_filters: if True, create templates for entity filters,
                        else mapping templates are created.
        default_values: if True, add default values for some fields.
    """
    assets_dir = BaseSettings.get().assets_dir
    schema_dir = assets_dir / "mappings" / "__schema__"
    template_dir = assets_dir / "mappings" / "__template__"

    for cls in EXTRACTED_MODEL_CLASSES:
        if entity_filters:
            schema_path = schema_dir / f"{cls.__name__}_EntityFilterSchema.json"
            template_path = (
                template_dir / "filters" / f"{cls.__name__}_EntityFilterTemplate.yaml"
            )
        else:
            schema_path = schema_dir / f"{cls.__name__}_MappingSchema.json"
            template_path = (
                template_dir / "mappings" / f"{cls.__name__}_MappingTemplate.yaml"
            )

        if not schema_path.exists():
            raise FileNotFoundError(
                f"Template cannot be created because the "
                f"corresponding mapping schema does not exist yet under the expected "
                f"path {schema_path}. Execute the schema generation before creating "
                f"templates."
            )

        generate_mapping_template_from_schema(
            schema_path, template_path, default_values
        )
        echo(
            f"Created template from schema {schema_path} "
            f"and saved under {template_path}."
        )


def mapping_templates() -> None:
    """Run automatic mapping template generation.

    With dynamic types for all MEx extracted model classes.
    """
    run_template_generation(entity_filters=False, default_values=True)


def entity_filter_templates() -> None:
    """Run automatic entity filter template generation.

    For all MEx extracted model classes.
    """
    run_template_generation(entity_filters=True, default_values=False)
