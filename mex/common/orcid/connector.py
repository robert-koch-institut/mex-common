from typing import Any

from mex.common.connector.http import HTTPConnector
from mex.common.exceptions import EmptySearchResultError, FoundMoreThanOneError
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


def get_data_by_id(orcid_id: str) -> dict[str, Any]:
    """Retrieve data by UNIQUE ORCID ID.

    Args:
        orcid_id: Uniqe identifier in ORCID system.

    Returns:
        Personal data of the single matching id.
    """
    orcidapi = OrcidConnector.get()
    # or endpoint = f"{orcid_id}/person"
    endpoint = f"{orcid_id}/record"
    return dict(orcidapi.request(method="GET", endpoint=endpoint))


def get_data_by_name(
    given_names: str = "*",
    family_name: str = "*",
    **filters: str,
) -> dict[str, Any]:
    """Get ORCID record of a single person for the given filters.

    Args:
        self: Connector.
        given_names: Given name of a person, defaults to non-null
        family_name: Surname of a person, defaults to non-null
        **filters: Key-value pairs representing ORCID search filters.

    Raises:
        EmptySearchResultError
        FoundMoreThanOneError

    Returns:
        Orcid data of the single matching person by name.
    """
    if given_names:
        filters["given-names"] = given_names
    if family_name:
        filters["family-name"] = family_name
    orcidapi = OrcidConnector.get()
    search_response = orcidapi.fetch(filters=filters)
    num_found = search_response.get("num-found", 0)
    if num_found == 0:
        msg = f"Cannot find orcid person for filters {filters}'"
        raise EmptySearchResultError(msg)
    if num_found > 1:
        msg = f"Found multiple orcid persons for filters {filters}'"
        raise FoundMoreThanOneError(msg)

    orcid_id = search_response["result"][0]["orcid-identifier"]["path"]
    return get_data_by_id(orcid_id)
