from abc import abstractmethod
from collections.abc import Generator, Iterable
from itertools import tee

from mex.common.connector import BaseConnector
from mex.common.models import AnyExtractedModel
from mex.common.settings import BaseSettings
from mex.common.types import Identifier


class BaseSink(BaseConnector):
    """Base class to define the interface of sink instances."""

    @abstractmethod
    def load(
        self, models: Iterable[AnyExtractedModel]
    ) -> Iterable[Identifier]:  # pragma: no cover
        """Iteratively load models to a destination and yield their identifiers."""
        ...


class MultiSink(BaseSink):
    """Sink to load models to multiple sinks simultaneously."""

    _sinks: list[BaseSink] = []

    def __init__(self) -> None:
        """Instantiate the multi sink singleton."""
        # break import cycle, sigh
        from mex.common.sinks.registry import _SINK_REGISTRY

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
        models: Iterable[AnyExtractedModel],
    ) -> Generator[Identifier, None, None]:
        """Load models to multiple sinks simultaneously."""
        for sink, model_gen in zip(
            self._sinks, tee(models, len(self._sinks)), strict=False
        ):
            yield from sink.load(model_gen)
