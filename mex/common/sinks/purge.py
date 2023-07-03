from typing import Any, Callable, Iterable, Union

from mex.common.exceptions import MExError
from mex.common.models.base import MExModel
from mex.common.public_api.models import PublicApiItem, PublicApiItemWithoutValues
from mex.common.settings import BaseSettings
from mex.common.sinks import Sink
from mex.common.sinks.ndjson import write_ndjson
from mex.common.sinks.public_api import (
    purge_items_from_public_api,
    purge_models_from_public_api,
)

PublicApiItemOptionalValues = Union[PublicApiItem, PublicApiItemWithoutValues]


def purge_items(items: Iterable[PublicApiItemOptionalValues]) -> None:
    """Purge items from the Public API or write to-be-purged items to NDJSON files.

    Args:
        items: Iterable of public API items

    Settings:
        sink: Where to purge the provided items
    """
    settings = BaseSettings.get()
    sink: Callable[[Iterable[PublicApiItemOptionalValues]], Iterable[Any]]
    if settings.sink == Sink.PUBLIC:
        sink = purge_items_from_public_api
    elif settings.sink == Sink.NDJSON:
        sink = write_ndjson
    else:
        raise MExError(f"Cannot purge from {settings.sink}")

    for _ in sink(items):
        continue  # unpacking the generator


def purge_models(models: Iterable[MExModel]) -> None:
    """Purge models from the Public API or write to-be-purged models to NDJSON files.

    Args:
        models: Iterable of MEx models

    Settings:
        sink: Where to purge the provided models
    """
    settings = BaseSettings.get()
    sink: Callable[[MExModel], Iterable[Any]]
    if settings.sink == Sink.PUBLIC:
        sink = purge_models_from_public_api
    elif settings.sink == Sink.NDJSON:
        sink = write_ndjson
    else:
        raise MExError(f"Cannot purge from {settings.sink}")

    for _ in sink(models):
        continue  # unpacking the generator
