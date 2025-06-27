import json
from collections.abc import Generator, Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TypeGuard

from requests import RequestException

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.logging import logger, watch
from mex.common.models import AnyExtractedModel, AnyMergedModel, AnyRuleSetResponse
from mex.common.settings import BaseSettings
from mex.common.sinks.base import BaseSink
from mex.common.utils import grouper


class BackendApiSink(BaseSink):
    """Sink to load models to the Backend API."""

    CONNECT_TIMEOUT: int | float = 5
    READ_TIMEOUT: int | float = 90

    def __init__(self) -> None:
        """Create a new sink."""
        settings = BaseSettings.get()
        self._executor = ThreadPoolExecutor(
            max_workers=settings.backend_api_parallelization,
            thread_name_prefix="backend_api_sink",
        )

    def close(self) -> None:
        """Close the sink."""
        self._executor.shutdown()

    @watch(log_interval=1000)
    def load(
        self,
        items: Iterable[AnyExtractedModel | AnyMergedModel | AnyRuleSetResponse],
    ) -> Generator[AnyExtractedModel | AnyMergedModel | AnyRuleSetResponse, None, None]:
        """Load extracted models or rule-sets to the Backend API using bulk insertion.

        Args:
            items: Iterable of extracted models or merged models or rule-sets

        Raises:
            NotImplementedError: When you try to load merged items into the backend

        Returns:
            Generator for posted models
        """
        settings = BaseSettings.get()
        futures = [
            self._executor.submit(BackendApiSink.load_chunk, chunk)
            for chunk in grouper(settings.backend_api_chunk_size, items)
        ]
        for future in as_completed(futures):
            yield from future.result()

    @staticmethod
    def is_supported(
        model_list: list[AnyExtractedModel | AnyMergedModel | AnyRuleSetResponse],
    ) -> TypeGuard[list[AnyExtractedModel | AnyRuleSetResponse]]:
        """Return whether the given list only contains models the backend can handle.

        The backend API can only handle extracted models and rule-set responses,
        not merged models. This type guard validates the input and provides
        type narrowing for downstream processing.

        Args:
            model_list: List of models to check for backend compatibility.

        Returns:
            True if all models are supported (extracted models or rule-set responses),
            False otherwise.
        """
        return all(
            isinstance(item, AnyExtractedModel | AnyRuleSetResponse)
            for item in model_list
        )

    @staticmethod
    def load_chunk(
        chunk: Iterable[AnyExtractedModel | AnyMergedModel | AnyRuleSetResponse | None],
    ) -> list[AnyExtractedModel | AnyRuleSetResponse]:
        """Load a chunk of models into the backend.

        Handles the actual bulk insertion of a chunk of models to the backend API.
        Filters out None values and validates that all models are supported before
        attempting ingestion.

        Args:
            chunk: Iterable of models to load, may contain None values.

        Raises:
            NotImplementedError: If the chunk contains unsupported model types.

        Returns:
            List of successfully loaded models.
        """
        connector = BackendApiConnector.get()
        model_list = [item for item in chunk if item is not None]
        if not BackendApiSink.is_supported(model_list):
            msg = "Backend can only ingest extracted models and rule-set responses."
            raise NotImplementedError(msg)
        try:
            connector.ingest(
                model_list,
                timeout=(BackendApiSink.CONNECT_TIMEOUT, BackendApiSink.READ_TIMEOUT),
            )
        except RequestException as error:
            model_info = [
                f"{m.entityType}(hadPrimarySource={m.hadPrimarySource}, "
                f"identifierInPrimarySource={m.identifierInPrimarySource}, ...)"
                if isinstance(m, AnyExtractedModel)
                else f"{m.entityType}(stableTargetId={m.stableTargetId})"
                for m in model_list
            ]
            logger.error(f"Error ingesting models: {', '.join(model_info)}")
            if error.response:
                response_body = json.dumps(error.response.json(), indent=4)
                logger.error(f"Backend responded: {response_body}")
            raise
        return model_list
