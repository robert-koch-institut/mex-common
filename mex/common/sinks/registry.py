from collections.abc import Generator, Iterable
from itertools import tee
from typing import Final

from mex.common.models import AnyExtractedModel, AnyMergedModel, AnyRuleSetResponse
from mex.common.settings import BaseSettings
from mex.common.sinks.backend_api import BackendApiSink
from mex.common.sinks.base import BaseSink
from mex.common.sinks.ndjson import NdjsonSink
from mex.common.types import Sink

_SINK_REGISTRY: Final[dict[Sink, type["BaseSink"]]] = {}


class _MultiSink(BaseSink):
    """Sink to load models to multiple sinks simultaneously."""

    # This class is private because it should only be acquired by calling `get_sink`.

    _sinks: list[BaseSink] = []

    def __init__(self) -> None:
        """Instantiate the multi sink singleton."""
        settings = BaseSettings.get()
        for sink in settings.sink:
            if sink in _SINK_REGISTRY:
                sink_cls = _SINK_REGISTRY[sink]
                self._sinks.append(sink_cls.get())
            else:
                msg = f"Sink function not implemented: {sink}"
                raise RuntimeError(msg)

    def close(self) -> None:
        """Close all underlying sinks."""
        for sink in self._sinks:
            sink.close()

    def load(
        self,
        items: Iterable[AnyExtractedModel | AnyMergedModel | AnyRuleSetResponse],
    ) -> Generator[AnyExtractedModel | AnyMergedModel | AnyRuleSetResponse, None, None]:
        """Load the given items to multiple sinks simultaneously."""
        for sink, model_gen in zip(
            self._sinks, tee(items, len(self._sinks)), strict=True
        ):
            yield from sink.load(model_gen)


def register_sink(key: Sink, sink_cls: type["BaseSink"]) -> None:
    """Register an implementation of a sink function to a settings key.

    Args:
        key: Possible value of `BaseSettings.sink`
        sink_cls: Implementation of the abstract sink class

    Raises:
        RuntimeError: When the `key` is already registered
    """
    if key in _SINK_REGISTRY:
        msg = f"Already registered sink function: {key}"
        raise RuntimeError(msg)
    _SINK_REGISTRY[key] = sink_cls


def get_sink() -> "BaseSink":
    """Get a sink function that serves all configured `sink` destinations.

    Raises:
        RuntimeError: When the configured sink is not registered

    Returns:
        A function that pours the models into all configured sinks
    """
    return _MultiSink.get()


# register the default providers shipped with mex-common
register_sink(Sink.BACKEND, BackendApiSink)
register_sink(Sink.NDJSON, NdjsonSink)
