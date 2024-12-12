from typing import Any

from mex.common.connector.http import HTTPConnector
from mex.common.settings import BaseSettings


class OrcidConnector(HTTPConnector):
    """Connector class for querying Orcid records."""

    TIMEOUT = 80

    def _set_url(self) -> None:
        """Set url of the host."""
        settings = BaseSettings.get()
        self.url = str(settings.orcid_api_url)

    def _check_availability(self) -> None:
        """Send a GET request to verify the host is available."""
        url = self.url + "search"
        response = self._send_request("HEAD", url=url, params={})
        response.raise_for_status()

    def check_orcid_id_exists(self, orcid_id: str) -> Any:
        """Search for an ORCID person by ORCID ID."""
        query = f"orcid:{orcid_id}"
        response = self.fetch(query)
        return response.get("num-found", 0) != 0

    @staticmethod
    def build_query(filters: dict[str, Any]) -> str:
        """Construct the ORCID API query string."""
        return " AND ".join([f"{key}:{value}" for key, value in filters.items()])

    def fetch(self, query: str) -> dict[str, Any]:
        """Perform a search query against the ORCID API."""
        endpoint = f"search/?q={query}"
        return self.request(method="GET", endpoint=endpoint)
