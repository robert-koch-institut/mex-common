from functools import cache
from typing import cast

from mex.common.connector.http import HTTPConnector
from mex.common.settings import BaseSettings

_PROPS = "info|aliases|labels|descriptions|datatype|claims|sitelinks|sitelinks/urls"


class WikidataQueryServiceConnector(HTTPConnector):
    """Connector class to handle requesting the Wikidata Query Service."""

    TIMEOUT = 80

    def _set_url(self) -> None:
        """Set url of the host."""
        settings = BaseSettings.get()
        self.url = str(settings.wiki_query_service_url)

    def _check_availability(self) -> None:
        """Send a GET request to verify the host is available."""
        self.request("GET", params={"format": "json"})

    @cache  # noqa: B019
    def get_data_by_query(self, query: str) -> list[dict[str, dict[str, str]]]:
        """Run provided query on wikidata using wikidata query service.

        Args:
            query (str): Wikidata query

        Returns:
            list: list of all items found
        """
        settings = BaseSettings.get()
        params = {"format": "json", "query": query}
        headers = {
            "User-Agent": f"{settings.mex_web_user_agent}",
            "Api-User-Agent": f"{settings.mex_web_user_agent}",
        }
        results = self.request("GET", params=params, headers=headers)
        return cast(list[dict[str, dict[str, str]]], results["results"]["bindings"])


class WikidataAPIConnector(HTTPConnector):
    """Connector class to handle requesting the Wikidata API."""

    def _set_url(self) -> None:
        """Set url of the host."""
        settings = BaseSettings.get()
        self.url = str(settings.wiki_api_url)

    def _check_availability(self) -> None:
        """Send a GET request to verify the host is available."""
        self.request(
            "GET", self.url, params={"format": "json", "action": "wbgetentities"}
        )

    @cache  # noqa: B019
    def get_wikidata_item_details_by_id(self, item_id: str) -> dict[str, str]:
        """Get details of a wikidata item by item id.

        Args:
            item_id (str): wikidata item id

        Returns:
            dict[str, Any]: details of the found item.
        """
        settings = BaseSettings.get()
        params = {
            "action": "wbgetentities",
            "format": "json",
            "ids": item_id,
            "props": _PROPS,
            "formatversion": "2",
        }
        headers = {
            "User-Agent": f"{settings.mex_web_user_agent}",
            "Api-User-Agent": f"{settings.mex_web_user_agent}",
        }
        results = self.request("GET", params=params, headers=headers)
        return cast(dict[str, str], results["entities"][item_id])
