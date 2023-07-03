import os

import numpy as np
import pandas
from pydantic import Field

from mex.common.cli import entrypoint
from mex.common.primary_source.extract import insert_primary_source_into_db
from mex.common.primary_source.models import SeedPrimarySource
from mex.common.settings import BaseSettings
from mex.common.transform import dromedary_to_snake
from mex.common.types import AssetsPath


class SeedScriptSettings(BaseSettings):
    """Custom settings for the seed script."""

    mappings_path: AssetsPath = Field(
        "mappings",
        description=(
            "Path to mappings where primary source CSV's are available, "
            "absolute path or relative to `assets_dir`."
        ),
    )


@entrypoint(SeedScriptSettings)
def insert_primary_sources_into_db() -> None:
    """Insert all primary sources data to database."""
    settings = SeedScriptSettings.get()

    for directory in os.listdir(settings.mappings_path):
        primary_source_csv = (
            settings.mappings_path.resolve() / directory / "primary-source.csv"
        )

        if (
            not os.path.isfile(primary_source_csv)
            or directory == "__all__"
            or directory == "__template__"
        ):
            continue

        df = pandas.read_csv(primary_source_csv, sep=";")
        df = df.replace(np.nan, None)

        primary_source = {}
        for _, row in df.iterrows():
            schema_property = row["json schema property"]
            value = row["expected default value"]

            multiple_values = []
            if not schema_property in primary_source:
                primary_source[dromedary_to_snake(schema_property)] = value
            else:
                multiple_values.append(primary_source[schema_property])
                if value:
                    multiple_values.append(value)
                primary_source[schema_property] = multiple_values

        primary_source["identifier"] = primary_source["identifier_in_primary_source"]

        insert_primary_source_into_db(SeedPrimarySource.parse_obj(primary_source))
