import json
from functools import cache

from mex.common.logging import logger
from mex.common.primary_source.models import SeedPrimarySource
from mex.common.settings import BaseSettings


@cache
def extract_seed_primary_sources() -> list[SeedPrimarySource]:
    """Extract seed primary sources from the raw-data JSON file.

    Settings:
        primary_sources_path: Resolved path to the primary sources file

    Returns:
        List of seed primary sources
    """
    settings = BaseSettings.get()
    with open(settings.primary_sources_path) as fh:
        seed_primary_sources = [
            SeedPrimarySource.model_validate(raw) for raw in json.load(fh)
        ]
    logger.info(f"extracted {len(seed_primary_sources)} seed primary sources")
    return seed_primary_sources
