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
        url = f"{self.url.rstrip('/')}/search"
        response = self._send_request("HEAD", url=url, params={})
        response.raise_for_status()

    def check_orcid_id_exists(self, orcid_id: str) -> bool:
        """Search for an ORCID person by ORCID ID."""
        query_dict = {"orcid": orcid_id}
        response = self.fetch(query_dict)
        return bool(response.get("num-found", 0))

    @staticmethod
    def build_query(filters: dict[str, Any]) -> str:
        """Construct the ORCID API query string."""
        return " AND ".join([f"{key}:{value}" for key, value in filters.items()])

    def fetch(self, filters: dict[str, Any]) -> dict[str, Any]:
        """Perform a search query against the ORCID API."""
        query = OrcidConnector.build_query(filters)
        return self.request(method="GET", endpoint="search", params={"q": query})
