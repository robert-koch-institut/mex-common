from itertools import tee
from typing import Any, Callable, Iterable

from mex.common.exceptions import MExError
from mex.common.models import MExModel
from mex.common.public_api.models import PublicApiItem, PublicApiItemWithoutValues
from mex.common.settings import BaseSettings
from mex.common.sinks.ndjson import write_ndjson
from mex.common.sinks.public_api import (
    purge_items_from_public_api,
    purge_models_from_public_api,
)
from mex.common.types import Sink

PublicApiItemOptionalValues = PublicApiItem | PublicApiItemWithoutValues


def purge_items(items: Iterable[PublicApiItemOptionalValues]) -> None:
    """Purge items from the Public API or write to-be-purged items to NDJSON files.

    Args:
        items: Iterable of public API items

    Settings:
        sink: Where to purge the provided items
    """
    settings = BaseSettings.get()
    func: Callable[[Iterable[PublicApiItemOptionalValues]], Iterable[Any]]

    for sink, item_gen in zip(settings.sink, tee(items, len(settings.sink))):
        if sink == Sink.PUBLIC:
            func = purge_items_from_public_api
        elif sink == Sink.NDJSON:
            func = write_ndjson
        else:
            raise MExError(f"Cannot purge from {sink}.")

        for _ in func(item_gen):
            continue  # unpacking the generator


def purge_models(models: Iterable[MExModel]) -> None:
    """Purge models from the Public API or write to-be-purged models to NDJSON files.

    Args:
        models: Iterable of MEx models

    Settings:
        sink: Where to purge the provided models
    """
    settings = BaseSettings.get()
    func: Callable[[MExModel], Iterable[Any]]

    for sink, model_gen in zip(settings.sink, tee(models, len(settings.sink))):
        if sink == Sink.PUBLIC:
            func = purge_models_from_public_api
        elif sink == Sink.NDJSON:
            func = write_ndjson
        else:
            raise MExError(f"Cannot purge from {sink}.")

        for _ in func(model_gen):
            continue  # unpacking the generator
