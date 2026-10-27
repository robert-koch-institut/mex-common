from collections.abc import Sequence
from typing import cast

from mex.common.connector.http import HTTPConnector
from mex.common.exceptions import EmptySearchResultError
from mex.common.settings import BaseSettings

WIKIDATA_MAX_BATCH_SIZE = 50  # maximum number of Q-numbers allowed for wikidata API


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

    def get_wikidata_item_details_by_ids(
        self,
        item_ids: Sequence[str],
    ) -> dict[str, dict[str, str]]:
        """Get multiple Wikidata items in a single API request."""
        if not item_ids:
            return {}

        if len(item_ids) > WIKIDATA_MAX_BATCH_SIZE:
            msg = (
                f"A Wikidata batch isn't allowed to contain more than "
                f"{WIKIDATA_MAX_BATCH_SIZE} IDs."
            )
            raise ValueError(msg)

        results = self.request(
            "GET",
            params={
                "action": "wbgetentities",
                "format": "json",
                "ids": "|".join(item_ids),
                "props": "labels|claims",
                "formatversion": "2",
            },
        )

        if error := results.get("error"):
            msg = f"Wikidata API error: {error}"
            raise RuntimeError(msg)

        entities = results.get("entities")
        if not isinstance(entities, dict):
            msg = "Wikidata API returned no entities mapping."
            raise TypeError(msg)

        missing_ids = [
            item_id
            for item_id in item_ids
            if item_id not in entities or entities[item_id].get("missing")
        ]

        if missing_ids:
            msg = f"Wikidata items not found: {missing_ids}"
            raise EmptySearchResultError(msg)

        return entities
