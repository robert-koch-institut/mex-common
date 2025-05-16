import json
import time
from abc import abstractmethod
from collections.abc import Mapping
from typing import Any, Literal, cast

import backoff
import requests
from requests import RequestException, Response, codes
from requests.exceptions import (
    ConnectTimeout,
    ProxyError,
    ReadTimeout,
    SSLError,
)

from mex.common.connector import BaseConnector
from mex.common.connector.utils import bounded_backoff
from mex.common.exceptions import (
    TimedReadTimeout,
    TimedServerError,
    TimedTooManyRequests,
)
from mex.common.logging import logger
from mex.common.settings import BaseSettings
from mex.common.transform import MExEncoder


class HTTPConnector(BaseConnector):
    """Base class for requests-based HTTP connectors."""

    TIMEOUT: int | float = 10
    TIMEOUT_MAX: int | float = 100
    PROPORTIONAL_BACKOFF_MIN: int | float = 3
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
        self._send_request("HEAD", self.url, params={})

    @backoff.on_exception(  # try to overcome network issues
        wait_gen=backoff.fibo,
        exception=(ConnectTimeout, ProxyError, SSLError),
        max_tries=3,
        jitter=backoff.random_jitter,
        logger=logger,
    )
    @backoff.on_exception(  # proportionally backoff on server fault
        wait_gen=backoff.runtime,
        exception=(TimedReadTimeout, TimedTooManyRequests, TimedServerError),
        value=bounded_backoff(PROPORTIONAL_BACKOFF_MIN, TIMEOUT_MAX),
        max_tries=5,
        jitter=backoff.random_jitter,
        logger=logger,
    )
    def _send_request(
        self,
        method: str,
        url: str,
        params: Mapping[str, list[str] | str | None] | None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Response:
        """Send the request with advanced retrying rules."""
        t0 = time.perf_counter()
        try:
            response = self.session.request(method, url, params, **kwargs)
            response.raise_for_status()
        except ReadTimeout as exc:
            raise TimedReadTimeout.create(exc, t0) from exc
        except RequestException as exc:
            if exc.response and exc.response.status_code >= codes.internal_server_error:
                raise TimedServerError.create(exc, t0) from exc
            if exc.response and exc.response.status_code == codes.too_many_requests:
                raise TimedTooManyRequests.create(exc, t0) from exc
            raise
        return response

    def request_raw(
        self,
        method: Literal["OPTIONS", "POST", "GET", "PUT", "DELETE"],
        endpoint: str | None = None,
        payload: Any = None,  # noqa: ANN401
        params: Mapping[str, list[str] | str | None] | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Response:
        """Prepare and send a raw request with error handling and payload serialization.

        Args:
            method: HTTP method to use
            endpoint: Path to API endpoint to be prefixed with host and version
            payload: Data to be serialized as JSON using the `MExEncoder`
            params: Dictionary to be sent in the query string of the request
            kwargs: Further keyword arguments passed to `requests`

        Raises:
            RequestException: Error from `requests` that can't be solved with a retry
            HTTPError: Re-raised HTTP error with (truncated) response body

        Returns:
            Response object for the  request
        """
        # Prepare request
        if endpoint:
            url = f"{self.url.rstrip('/')}/{endpoint.lstrip('/')}"
        else:
            url = self.url
        kwargs.setdefault("timeout", self.TIMEOUT)
        if not kwargs.get("headers"):
            kwargs.setdefault("headers", {})
        kwargs["headers"].setdefault("User-Agent", "rki/mex")

        if payload:
            kwargs["data"] = json.dumps(payload, cls=MExEncoder)

        # Send request
        return self._send_request(method, url, params, **kwargs)

    def request(
        self,
        method: Literal["OPTIONS", "POST", "GET", "PUT", "DELETE"],
        endpoint: str | None = None,
        payload: Any = None,  # noqa: ANN401
        params: Mapping[str, list[str] | str | None] | None = None,
        **kwargs: Any,  # noqa: ANN401
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
        if not kwargs.get("headers"):
            kwargs.setdefault("headers", {})
        kwargs["headers"].setdefault("Accept", "application/json")
        response = self.request_raw(
            method, endpoint=endpoint, payload=payload, params=params, **kwargs
        )
        if response.status_code == codes.no_content:
            return {}
        return cast("dict[str, Any]", response.json())

    def close(self) -> None:
        """Close the connector's underlying requests session."""
        self.session.close()
