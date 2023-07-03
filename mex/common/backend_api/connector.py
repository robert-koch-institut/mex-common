import json
from itertools import groupby
from typing import Any, Literal, TypeVar, cast
from urllib.parse import urljoin

import backoff
from requests import Response, Session
from requests.exceptions import HTTPError, RequestException

from mex.common.backend_api.models import BulkInsertResponse
from mex.common.connector import BaseConnector
from mex.common.models.base import MExModel
from mex.common.settings import BaseSettings
from mex.common.transform import MExEncoder
from mex.common.types import Identifier

ModelT = TypeVar("ModelT", bound=MExModel)


class BackendApiConnector(BaseConnector):
    """Connector class to handle interaction with the Backend API."""

    TIMEOUT = 10
    API_VERSION = "v0"

    def __init__(self, settings: BaseSettings) -> None:
        """Create a new Backend API connection.

        Args:
            settings: Configured settings instance
        """
        self.session = Session()
        self.session.headers["Accept"] = "application/json"
        self.session.headers["User-Agent"] = "rki/mex"
        self.session.verify = settings.verify_session  # type: ignore
        self.url = settings.backend_api_url
        self._check_availability()

    def _check_availability(self) -> None:
        """Send a GET request to verify the API is available."""
        self.request("GET", "_system/check")

    def request(
        self,
        method: Literal["OPTIONS", "POST", "GET", "PUT", "DELETE"],
        endpoint: str,
        payload: Any = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Prepare and send a request with error handling and payload de/serialization.

        Args:
            method: HTTP method to use
            endpoint: Path to API endpoint to be prefixed with host and version
            payload: Data to be serialized as JSON using the `MExEncoder`
            kwargs: Further keyword arguments passed to `requests`

        Raises:
            RequestException: Error from `requests` that can't be solved with a retry
            HTTPError: Re-raised HTTP error with (truncated) response body
            JSONDecodeError: If body of response cannot be parsed correctly

        Returns:
            Parsed JSON body of the response
        """
        # Prepare request
        url = urljoin(self.url, f"{self.API_VERSION}/{endpoint}")
        kwargs.setdefault("timeout", self.TIMEOUT)
        if payload:
            kwargs.setdefault("headers", {})
            kwargs["data"] = json.dumps(payload, cls=MExEncoder)
            kwargs["headers"].setdefault("Content-Type", "application/json")

        # Send request
        response = self._send_request(method, url, **kwargs)

        try:
            response.raise_for_status()
        except HTTPError as error:
            # Re-raise errors that outlived the retries and add the response body
            raise HTTPError(
                " ".join(str(arg) for arg in (*error.args, response.text[:4096])),
                response=response,
            ) from error

        if response.status_code == 204:
            return {}
        return cast(dict[str, Any], response.json())

    @backoff.on_predicate(
        backoff.fibo,
        lambda response: cast(Response, response).status_code >= 500,
        max_tries=4,
    )
    @backoff.on_exception(backoff.fibo, RequestException, max_tries=6)
    def _send_request(self, method: str, url: str, **kwargs: Any) -> Response:
        """Send the response with advanced retrying ruleset."""
        return self.session.request(method, url, **kwargs)

    def close(self) -> None:
        """Close the connector's underlying requests session."""
        self.session.close()

    def post_models(self, models: list[MExModel]) -> list[Identifier]:
        """Post models to Backend API in a bulk insertion request.

        Args:
            models: MEx models to post

        Raises:
            HTTPError: If insert was not accepted, crashes or times out

        Returns:
            Identifiers of posted models
        """
        response = self.request(
            "POST",
            "entity",
            {
                entity_type: list(entities)
                for entity_type, entities in groupby(
                    sorted(models, key=lambda e: e.get_entity_type()),
                    lambda e: e.get_entity_type(),
                )
            },
        )
        insert_response = BulkInsertResponse.parse_obj(response)
        return insert_response.identifiers
