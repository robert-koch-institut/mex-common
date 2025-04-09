import json
import time
from abc import abstractmethod
from collections.abc import Mapping
from typing import Any, Literal, cast

import backoff
import requests
from requests import Response, codes
from requests.exceptions import (
    ConnectTimeout,
    HTTPError,
    ProxyError,
    ReadTimeout,
    SSLError,
)

from mex.common.connector import BaseConnector
from mex.common.exceptions import TimedReadTimeout
from mex.common.logging import logger
from mex.common.settings import BaseSettings
from mex.common.transform import MExEncoder


class HTTPConnector(BaseConnector):
    """Base class for requests-based HTTP connectors."""

    TIMEOUT: int | float = 10
    TIMEOUT_MAX: int | float = 100
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
        self.session.verify = settings.verify_session  # type: ignore[assignment]

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
        params: Mapping[str, list[str] | str | None] | None = None,
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
        kwargs["headers"].setdefault("User-Agent", "rki/mex")

        if payload:
            kwargs["data"] = json.dumps(payload, cls=MExEncoder)

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

        if response.status_code == codes.no_content:
            return {}
        return cast("dict[str, Any]", response.json())

    @backoff.on_predicate(
        backoff.fibo,
        lambda response: cast("Response", response).status_code
        >= codes.internal_server_error
        or cast("Response", response).status_code == codes.too_many_requests,
        max_tries=3,
        jitter=backoff.random_jitter,
        logger=logger,
    )
    @backoff.on_predicate(
        backoff.fibo,
        lambda response: cast("Response", response).status_code == codes.forbidden,
        max_tries=1,
        jitter=backoff.random_jitter,
        logger=logger,
    )
    @backoff.on_exception(
        backoff.fibo,
        (ConnectTimeout, ProxyError, SSLError),
        max_tries=3,
        jitter=backoff.random_jitter,
        logger=logger,
    )
    @backoff.on_exception(
        backoff.runtime,  # proportional backoff
        TimedReadTimeout,
        value=lambda error: min(
            cast("TimedReadTimeout", error).seconds, HTTPConnector.TIMEOUT_MAX
        ),
        max_tries=5,
        jitter=backoff.random_jitter,
        logger=logger,
    )
    def _send_request(
        self,
        method: str,
        url: str,
        params: Mapping[str, list[str] | str | None] | None,
        **kwargs: Any,
    ) -> Response:
        """Send the response with advanced retrying rules."""
        t0 = time.perf_counter()
        try:
            return self.session.request(method, url, params, **kwargs)
        except ReadTimeout as error:
            # wrap error in a custom timed error to get proportional backoff
            raise TimedReadTimeout(
                *error.args,
                response=error.response,
                request=error.request,
                seconds=time.perf_counter() - t0,
            ) from error

    def close(self) -> None:
        """Close the connector's underlying requests session."""
        self.session.close()
