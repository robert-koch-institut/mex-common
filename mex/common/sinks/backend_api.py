from collections.abc import Generator, Iterable

from requests import RequestException

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.logging import logger, watch
from mex.common.models import AnyExtractedModel, AnyMergedModel, AnyRuleSetResponse
from mex.common.sinks.base import BaseSink
from mex.common.utils import grouper


class BackendApiSink(BaseSink):
    """Sink to load models to the Backend API."""

    CHUNK_SIZE: int = 25
    CONNECT_TIMEOUT: int | float = 5
    READ_TIMEOUT: int | float = 30

    @watch(log_interval=1000)
    def load(
        self, items: Iterable[AnyExtractedModel | AnyMergedModel | AnyRuleSetResponse]
    ) -> Generator[AnyExtractedModel | AnyMergedModel | AnyRuleSetResponse, None, None]:
        """Load extracted models or rule-sets to the Backend API using bulk insertion.

        Args:
            items: Iterable of extracted models or merged models or rule-sets

        Raises:
            NotImplementedError: When you try to load merged items into the backend

        Returns:
            Generator for posted models
        """
        connector = BackendApiConnector.get()
        for chunk in grouper(self.CHUNK_SIZE, items):
            model_list: list[AnyExtractedModel | AnyRuleSetResponse] = []
            for model in chunk:
                if isinstance(model, AnyExtractedModel | AnyRuleSetResponse):
                    model_list.append(model)
                elif model is not None:
                    msg = f"backend cannot ingest {type(model)}"
                    raise NotImplementedError(msg)
            try:
                response = connector.ingest(
                    model_list,
                    timeout=(self.CONNECT_TIMEOUT, self.READ_TIMEOUT),
                )
            except RequestException:
                model_info = [
                    f"{m.entityType}:{m.hadPrimarySource}:{m.identifierInPrimarySource}"
                    if isinstance(m, AnyExtractedModel)
                    else f"{m.entityType}:{m.stableTargetId}"
                    for m in model_list
                ]
                logger.error(f"error ingesting models: {', '.join(model_info)}")
                raise
            yield from response
