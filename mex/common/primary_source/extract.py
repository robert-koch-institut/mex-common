import json
from typing import Generator

from mex.common.logging import watch
from mex.common.primary_source.models import SeedPrimarySource
from mex.common.settings import BaseSettings


@watch
def extract_seed_primary_sources() -> Generator[SeedPrimarySource, None, None]:
    """Extract seed primary sources from the raw-data JSON file.

    Settings:
        primary_sources_path: Resolved path to the primary sources file

    Returns:
        Generator for seed primary sources
    """
    settings = BaseSettings.get()
    with open(settings.primary_sources_path, "r") as fh:
        for raw in json.load(fh):
            yield SeedPrimarySource.model_validate(raw)
