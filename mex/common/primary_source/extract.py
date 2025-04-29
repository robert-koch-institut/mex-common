import json
from functools import lru_cache

from mex.common.logging import logger
from mex.common.primary_source.models import SeedPrimarySource
from mex.common.settings import BaseSettings


@lru_cache(maxsize=1)
def extract_seed_primary_sources() -> list[SeedPrimarySource]:
    """Extract seed primary sources from the raw-data JSON file.

    Settings:
        primary_sources_path: Resolved path to the primary sources file

    Returns:
        List of seed primary sources
    """
    settings = BaseSettings.get()
    with open(settings.primary_sources_path) as fh:
        raw_units = json.load(fh)
    logger.info("extracted %s seed primary sources", len(raw_units))
    return [SeedPrimarySource.model_validate(raw) for raw in raw_units]
