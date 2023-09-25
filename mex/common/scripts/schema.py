import json

from pydantic import Field
from pydantic.json_schema import models_json_schema

from mex.common.cli import entrypoint
from mex.common.logging import echo
from mex.common.models import EXTRACTED_MODEL_CLASSES
from mex.common.settings import BaseSettings
from mex.common.transform import MExEncoder
from mex.common.types import WorkPath


class SchemaScriptsSettings(BaseSettings):
    """Settings for schema-related scripts."""

    json_file: WorkPath = Field(
        WorkPath("schema.json"),
        description=(
            "Path to json schema file to write, absolute or relative to `work_dir`."
        ),
    )
    schema_title: str = Field(
        "MEx Metadata Schema",
        description="Title for JSON schema export.",
    )


@entrypoint(SchemaScriptsSettings)
def dump_schema() -> None:
    """Dump a JSON schema of the current MEx models.

    Settings:
        json_file: Path to the schema.json file
        schema_title: Title to use for the schema
    """
    settings = SchemaScriptsSettings.get()
    _, mex_schema = models_json_schema(
        models=[(m, "validation") for m in EXTRACTED_MODEL_CLASSES],
        title=settings.schema_title,
        ref_template="#/definitions/{model}",
    )

    with open(settings.json_file, "w", encoding="utf-8") as fh:
        json.dump(mex_schema, fh, indent=2, sort_keys=True, cls=MExEncoder)

    echo(f"[dump schema] {settings.json_file}", fg="green")
