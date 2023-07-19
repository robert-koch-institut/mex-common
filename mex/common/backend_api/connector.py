from itertools import groupby
from urllib.parse import urljoin

from mex.common.backend_api.models import BulkInsertResponse
from mex.common.connector import HTTPConnector
from mex.common.models import MExModel
from mex.common.models.base import MExModel
from mex.common.settings import BaseSettings
from mex.common.types import Identifier


class BackendApiConnector(HTTPConnector):
    """Connector class to handle interaction with the Backend API."""

    API_VERSION = "v0"

    def _check_availability(self) -> None:
        """Send a GET request to verify the API is available."""
        self.request("GET", "_system/check")

    def _set_url(self, settings: BaseSettings) -> None:
        self.url = urljoin(settings.backend_api_url, self.API_VERSION)

    def post_models(self, models: list[MExModel]) -> list[Identifier]:
        """Post models to Backend API in a bulk insertion request.

        Args:
            models: Extracted or merged models to post

        Raises:
            HTTPError: If insert was not accepted, crashes or times out

        Returns:
            Identifiers of posted models
        """
        response = self.request(
            "POST",
            "ingest",
            {
                entity_type: list(entities)
                for entity_type, entities in groupby(
                    sorted(models, key=lambda e: e.get_entity_type()),
                    lambda e: e.get_entity_type(),
                )
            },
        )
        insert_response = BulkInsertResponse.parse_obj(response)
        return insert_response.identifiers
