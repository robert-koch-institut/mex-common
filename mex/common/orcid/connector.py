from typing import Any

from mex.common.connector.http import HTTPConnector
from mex.common.exceptions import EmptySearchResultError, FoundMoreThanOneError
from mex.common.settings import BaseSettings


class OrcidConnector(HTTPConnector):
    """Connector class for querying Orcid records."""

    def _set_url(self) -> None:
        """Set url of the host."""
        settings = BaseSettings.get()
        self.url = str(settings.orcid_api_url)

    def _check_availability(self) -> None:
        """Send a GET request to verify the host is available."""
        url = f"{self.url.rstrip('/')}/search"
        response = self._send_request("HEAD", url=url, params={})
        response.raise_for_status()

    def build_query(self, filters: dict[str, Any]) -> str:
        """Construct the ORCID API query string."""
        return " AND ".join([f"{key}:{value}" for key, value in filters.items()])

    def fetch(self, filters: dict[str, Any]) -> dict[str, Any]:
        """Perform a search query against the ORCID API."""
        query = self.build_query(filters)
        return self.request(method="GET", endpoint="search", params={"q": query})

    def get_data_by_id(self, orcid_id: str) -> dict[str, Any]:
        """Retrieve data by UNIQUE ORCID ID.

        Args:
            orcid_id: Unique identifier in ORCID system.

        Returns:
            Personal data of the single matching id.
        """
        # or endpoint = f"{orcid_id}/person"
        endpoint = f"{orcid_id}/record"
        return dict(self.request(method="GET", endpoint=endpoint))

    def get_data_by_name(
        self,
        given_names: str = "*",
        family_name: str = "*",
        given_and_family_names: str = "*",
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Get ORCID record of a single person for the given filters.

        Args:
            self: Connector.
            given_names: Given name of a person, defaults to non-null
            family_name: Surname of a person, defaults to non-null
            given_and_family_names: Name of person, default to non-null
            filters: Key-value pairs representing ORCID search filters.

        Raises:
            EmptySearchResultError
            FoundMoreThanOneError

        Returns:
            Orcid data of the single matching person by name.
        """
        if filters is None:
            filters = {}
        if given_names != "*":
            filters["given-names"] = given_names
        if family_name != "*":
            filters["family-name"] = family_name
        if given_and_family_names != "*":
            filters["given-and-family-names"] = given_and_family_names

        search_response = self.fetch(filters)

        num_found = search_response.get("num-found", 0)
        if num_found == 0:
            msg = "Cannot find orcid person for filters.'"
            raise EmptySearchResultError(msg)
        if num_found > 1:
            msg = "Found multiple orcid persons for filters.'"
            raise FoundMoreThanOneError(msg)

        orcid_id = search_response["result"][0]["orcid-identifier"]["path"]
        return self.get_data_by_id(orcid_id=orcid_id)
