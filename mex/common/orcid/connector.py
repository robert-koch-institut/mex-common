from typing import Any

from mex.common.connector.http import HTTPConnector
from mex.common.settings import BaseSettings


class OrcidConnector(HTTPConnector):  # noqa: D101
    # TODO:  # noqa: TD002
    # oauth with orcid sandbox to get oauth code
    # get read-public key
    # OrcidPerson class
    # refine session and requests for person here

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

    def _check_orcid_id_exists(self, orcid_id: str) -> Any:
        """Search for an ORCID person by ORCID ID."""
        query = f"orcid:{orcid_id}"
        endpoint = f"search/?q={query}"
        response = self.request(method="GET", endpoint=endpoint)
        return response.get("num-found", 0) != 0

    def get_personal_metadata_by_id(self, orcid_id: str) -> dict[str, Any]:
        """Retrieve personal details by UNIQUE ORCID ID."""
        if self._check_orcid_id_exists(orcid_id):
            endpoint = f"{orcid_id}/record"
            return self.request(method="GET", endpoint=endpoint)
        return {"result": None, "num-found": 0}

    def _search_person_by_name(
        self, family_name: str, given_names: str
    ) -> dict[str, Any]:
        """Search for a person by family name and given names."""
        query = f"family-name:{family_name} AND given-names:{given_names}"

        endpoint = f"search/?q={query}"
        return self.request(method="GET", endpoint=endpoint)

    def get_personal_metadata_by_name(
        self, family_name: str, given_names: str
    ) -> dict[str, Any]:
        """Search for person by orcid ID and retrieve personal details by ORCID ID."""
        search_response = self._search_person_by_name(
            family_name=family_name, given_names=given_names
        )
        num_found = search_response.get("num-found", 0)
        if num_found == 1:
            orcid_id = search_response["result"][0]["orcid-identifier"]["path"]
            return self.get_personal_metadata_by_id(orcid_id)
        return {"result": None, "num-found": 0}

    def list_person_by_name(self, family_name: str, given_names: str) -> dict[str, Any]:  # noqa: D102
        return self._search_person_by_name(
            family_name=family_name, given_names=given_names
        )
