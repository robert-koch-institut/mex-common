from urllib.parse import urljoin

from mex.common.backend_api.models import BulkInsertResponse
from mex.common.connector import HTTPConnector
from mex.common.models import AnyExtractedModel
from mex.common.settings import BaseSettings
from mex.common.types import AnyExtractedIdentifier


class BackendApiConnector(HTTPConnector):
    """Connector class to handle interaction with the Backend API."""

    API_VERSION = "v0"

    def _check_availability(self) -> None:
        """Send a GET request to verify the API is available."""
        self.request("GET", "_system/check")

    def _set_authentication(self) -> None:
        """Set the backend API key to all session headers."""
        settings = BaseSettings.get()
        self.session.headers["X-API-Key"] = settings.backend_api_key.get_secret_value()

    def _set_url(self) -> None:
        """Set the backend api url with the version path."""
        settings = BaseSettings.get()
        self.url = urljoin(str(settings.backend_api_url), self.API_VERSION)

    def post_models(
        self, models: list[AnyExtractedModel]
    ) -> list[AnyExtractedIdentifier]:
        """Post models to Backend API in a bulk insertion request.

        Args:
            models: Extracted or merged models to post

        Raises:
            HTTPError: If insert was not accepted, crashes or times out

        Returns:
            Identifiers of posted extracted models
        """
        response = self.request(
            method="POST", endpoint="ingest", payload={"items": models}
        )
        insert_response = BulkInsertResponse.model_validate(response)
        return insert_response.identifiers
