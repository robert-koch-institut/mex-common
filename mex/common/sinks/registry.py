from typing import Final

from mex.common.sinks.backend_api import BackendApiSink
from mex.common.sinks.base import BaseSink
from mex.common.sinks.ndjson import NdJsonSink
from mex.common.types import Sink

_SINK_REGISTRY: Final[dict[Sink, type[BaseSink]]] = {}


def register_sink(key: Sink, sink_cls: type[BaseSink]) -> None:
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


def get_sink() -> BaseSink:
    """Get a sink function that serves all configured `sink` destinations.

    Raises:
        RuntimeError: When the configured sink is not registered

    Returns:
        A function that pours the models into all configured sinks
    """
    # break import cycle, sigh
    from mex.common.sinks.base import MultiSink

    return MultiSink.get()


# register the default providers shipped with mex-common
register_sink(Sink.BACKEND, BackendApiSink)
register_sink(Sink.NDJSON, NdJsonSink)
