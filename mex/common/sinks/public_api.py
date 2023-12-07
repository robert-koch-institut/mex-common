from typing import Generator, Iterable

from mex.common.logging import watch
from mex.common.models import MExModel
from mex.common.public_api.connector import PublicApiConnector
from mex.common.public_api.models import PublicApiItem, PublicApiItemWithoutValues
from mex.common.types import Identifier
from mex.common.utils import grouper


@watch
def post_to_public_api(
    models: Iterable[MExModel], chunk_size: int = 100
) -> Generator[Identifier, None, None]:
    """Load models to the Public API using bulk insertion.

    Args:
        models: Iterable of extracted or merged models
        chunk_size: Optional size to chunks to post in one request

    Returns:
        Generator for identifiers of posted models
    """
    connector = PublicApiConnector.get()
    for chunk in grouper(chunk_size, models):
        model_list = list(filter(None, chunk))
        yield from connector.post_models(model_list)


@watch
def purge_models_from_public_api(
    models: Iterable[MExModel],
) -> Generator[str, None, None]:
    """Purge models from Public API.

    Args:
        models: list of MEx models

    Returns:
        Generator for status messages per model
    """
    connector = PublicApiConnector.get()
    for model in models:
        api_id = connector.delete_model(model)
        yield f"purged item {api_id} for {model.__class__.__name__} {model.identifier}"


@watch
def purge_items_from_public_api(
    items: Iterable[PublicApiItem | PublicApiItemWithoutValues],
) -> Generator[str, None, None]:
    """Purge items from Public API.

    Args:
        items: list of Public API items

    Returns:
        Generator for status messages per model
    """
    connector = PublicApiConnector.get()
    for item in items:
        api_id = connector.delete_item(item)
        yield f"purged item {api_id} for {item.entityType}"
