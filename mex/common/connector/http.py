import json
from abc import abstractmethod
from typing import Any, Literal, cast

import backoff
import requests
from requests import HTTPError, RequestException, Response

from mex.common.connector import BaseConnector
from mex.common.settings import BaseSettings
from mex.common.transform import MExEncoder


class HTTPConnector(BaseConnector):
    """Base class for requests-based HTTP connectors."""

    TIMEOUT = 10

    url: str = ""

    def __init__(self) -> None:
        """Create a new http connection."""
        self._set_session()
        self._set_url()
        self._set_authentication()
        self._check_availability()

    def _set_session(self) -> None:
        """Create and set request session."""
        settings = BaseSettings.get()
        self.session = requests.Session()
        self.session.verify = settings.verify_session  # type: ignore

    def _set_authentication(self) -> None:
        """Authenticate to the host."""

    @abstractmethod
    def _set_url(self) -> None:
        """Set url of the host."""

    def _check_availability(self) -> None:
        """Send a GET request to verify the host is available."""
        response = self._send_request("HEAD", self.url, params={})
        response.raise_for_status()

    def request(
        self,
        method: Literal["OPTIONS", "POST", "GET", "PUT", "DELETE"],
        endpoint: str | None = None,
        payload: Any = None,
        params: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Prepare and send a request with error handling and payload de/serialization.

        Args:
            method: HTTP method to use
            endpoint: Path to API endpoint to be prefixed with host and version
            payload: Data to be serialized as JSON using the `MExEncoder`
            params: Dictionary to be sent in the query string of the request
            kwargs: Further keyword arguments passed to `requests`

        Raises:
            RequestException: Error from `requests` that can't be solved with a retry
            HTTPError: Re-raised HTTP error with (truncated) response body
            JSONDecodeError: If body of response cannot be parsed correctly

        Returns:
            Parsed JSON body of the response
        """
        # Prepare request
        if endpoint:
            url = f"{self.url.rstrip('/')}/{endpoint.lstrip('/')}"
        else:
            url = self.url
        kwargs.setdefault("timeout", self.TIMEOUT)
        if not kwargs.get("headers"):
            kwargs.setdefault("headers", {})
        kwargs["headers"].setdefault("Accept", "application/json")

        if payload:
            kwargs["data"] = json.dumps(payload, cls=MExEncoder)
            kwargs["headers"].setdefault("User-Agent", "rki/mex")

        # Send request
        response = self._send_request(method, url, params, **kwargs)
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
    @backoff.on_predicate(
        backoff.fibo,
        lambda response: cast(Response, response).status_code == 429,
        max_tries=10,
    )
    @backoff.on_predicate(
        backoff.fibo,
        lambda response: cast(Response, response).status_code == 403,
        max_tries=10,
    )
    @backoff.on_exception(backoff.fibo, RequestException, max_tries=6)
    def _send_request(
        self, method: str, url: str, params: dict[str, str] | None, **kwargs: Any
    ) -> Response:
        """Send the response with advanced retrying rules."""
        return self.session.request(method, url, params, **kwargs)

    def close(self) -> None:
        """Close the connector's underlying requests session."""
        self.session.close()
