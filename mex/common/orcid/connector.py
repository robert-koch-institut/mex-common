from typing import Any

from mex.common.connector.http import HTTPConnector
from mex.common.orcid.models import OrcidRecord, OrcidSearchResponse
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

    def get_record_by_id(self, orcid_id: str) -> OrcidRecord:
        """Get a single orcid record by id.

        Args:
            orcid_id: Unique identifier in ORCID system.

        Returns:
            Orcid record of the single matching id.
        """
        endpoint = f"{orcid_id}/record"
        response = self.request(method="GET", endpoint=endpoint)
        return OrcidRecord.model_validate(response)

    def search_records_by_name(  # noqa: PLR0913
        self,
        given_names: str | None = None,
        family_name: str | None = None,
        given_and_family_names: str | None = None,
        filters: dict[str, Any] | None = None,
        skip: int = 0,
        limit: int = 10,
    ) -> OrcidSearchResponse:
        """Search for orcid results for the given filters.

        Args:
            given_names: Optional given name of a person.
            family_name: Optional surname of a person.
            given_and_family_names: Optional full name of a person.
            filters: Key-value pairs representing ORCID search filters.
            skip: How many items to skip for pagination.
            limit: How many items to return in one page.

        Returns:
            Paginated list of orcid results.
        """
        if filters is None:
            filters = {}
        if given_names and (n := given_names.strip()):
            filters["given-names"] = n
        if family_name and (n := family_name.strip()):
            filters["family-name"] = n
        if given_and_family_names and (n := given_and_family_names.strip()):
            filters["given-and-family-names"] = n
        query = self.build_query(filters)
        params = {"q": query or None, "start": str(skip), "rows": str(limit)}
        response = self.request(method="GET", endpoint="search", params=params)
        return OrcidSearchResponse.model_validate(response)
