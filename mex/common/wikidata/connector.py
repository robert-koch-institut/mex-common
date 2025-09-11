from typing import cast

from mex.common.connector.http import HTTPConnector
from mex.common.exceptions import EmptySearchResultError
from mex.common.settings import BaseSettings


class WikidataAPIConnector(HTTPConnector):
    """Connector class to handle requesting the Wikidata API."""

    def _set_url(self) -> None:
        """Set url of the host."""
        settings = BaseSettings.get()
        self.url = str(settings.wiki_api_url)

    def _set_session(self) -> None:
        """Create and set request session."""
        super()._set_session()
        settings = BaseSettings.get()
        self.session.headers.update(
            {
                "User-Agent": settings.mex_web_user_agent,
                "Api-User-Agent": settings.mex_web_user_agent,
            }
        )

    def _check_availability(self) -> None:
        """Send a GET request to verify the host is available."""
        self.request("GET", params={"format": "json", "action": "wbgetentities"})

    def get_wikidata_item_details_by_id(self, item_id: str) -> dict[str, str]:
        """Get details of a wikidata item by item id.

        Args:
            item_id: wikidata item id

        Returns:
            Details of the found item.
        """
        results = self.request(
            "GET",
            params={
                "action": "wbgetentities",
                "format": "json",
                "ids": item_id,
                "props": (
                    "info|aliases|labels|descriptions|datatype|claims|"
                    "sitelinks|sitelinks/urls"
                ),
                "formatversion": "2",
            },
        )
        if entities := results.get("entities"):
            return cast("dict[str, str]", entities[item_id])
        if (error := results.get("error")) and error["code"] == "no-such-entity":
            raise EmptySearchResultError(error["info"])
        msg = f"unexpected error getting wikidata item: {item_id}"
        raise RuntimeError(msg)
