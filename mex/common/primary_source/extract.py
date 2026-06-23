import json
from functools import lru_cache

from mex.common.assets import get_assets_connector
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
    file_contents = get_assets_connector().load_file(settings.primary_sources_path)
    raw_units = json.loads(file_contents.decode('utf-8'))
    logger.info("extracted %s seed primary sources", len(raw_units))
    return [SeedPrimarySource.model_validate(raw) for raw in raw_units]
