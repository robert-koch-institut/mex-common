from functools import cache
from typing import Any, cast

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from mex.common.connector import BaseConnector
from mex.common.exceptions import MExError
from mex.common.settings import BaseSettings


class WikidataConnector(BaseConnector):
    """Connector class to handle requesting the Wikidata API."""

    TIMEOUT = 80
    DEFAULT_RETRIES = 10
    DEFAULT_BACKOFF = 1.5

    def __init__(self, settings: BaseSettings):
        """Create a new Wikidata connection.

        Args:
            settings: Configured settings instance
        """
        self.session = self._get_session_with_retries()
        self.api_url = settings.wiki_api_url
        self.query_service_url = settings.wiki_query_service_url

        self._check_availability()

    def _check_availability(self) -> None:
        response = self.session.get(self.query_service_url, timeout=self.TIMEOUT)
        if response.ok:
            return
        raise MExError(response.text)

    def _get_json_from_api(
        self, url: str, params: dict[str, Any]
    ) -> dict[str, dict[str, str]]:
        response = self.session.get(url=url, params=params, timeout=self.TIMEOUT)

        return cast(dict[str, dict[str, str]], response.json())

    @cache
    def get_data_by_query(self, query: str) -> list[dict[str, dict[str, str]]]:
        """Run provided query on wikidata using wikidata query service.

        Args:
            query (str): Wikidata query

        Returns:
            list: list of all items found
        """
        params = {"format": "json", "query": query}

        results = self._get_json_from_api(url=self.query_service_url, params=params)

        return results["results"]["bindings"]  # type: ignore

    @cache
    def get_wikidata_item_details_by_id(self, item_id: str) -> dict[str, str]:
        """Get details of a wikidata item by item id.

        Args:
            item_id (str): wikidata item id

        Returns:
            dict[str, Any]: details of the found item.
        """
        params = {
            "action": "wbgetentities",
            "format": "json",
            "ids": item_id,
            "props": "info|aliases|labels|descriptions|datatype|claims|sitelinks|sitelinks/urls",
            "formatversion": "2",
        }

        results = self._get_json_from_api(url=self.api_url, params=params)

        return results["entities"][item_id]  # type: ignore

    def _get_session_with_retries(
        self,
        max_retries: int = DEFAULT_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF,
    ) -> requests.Session:
        """Create a new Session with `max_retries` retry attempts at multiple status codes.

        Args:
            max_retries (int, optional): max retries in case of failure. Defaults to DEFAULT_RETRIES.
            backoff_factor (float, optional): Wait in seconds before a retry. Defaults to DEFAULT_BACKOFF.

        Returns:
            requests.Session: session with retries
        """
        new_session = requests.Session()
        retries = Retry(
            total=max_retries,
            allowed_methods=frozenset(["GET"]),
            status_forcelist=frozenset([429, 500, 502, 503, 504]),
            backoff_factor=backoff_factor,
        )

        retry_adapter = HTTPAdapter(max_retries=retries)
        new_session.mount("http://", retry_adapter)
        new_session.mount("https://", retry_adapter)

        return new_session

    def close(self) -> None:
        """Close the connector's underlying requests session."""
        self.session.close()
