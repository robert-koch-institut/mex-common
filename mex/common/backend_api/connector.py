from urllib.parse import urljoin

from requests.exceptions import HTTPError

from mex.common.backend_api.models import (
    ExtractedItemsRequest,
    ExtractedItemsResponse,
    IdentifiersResponse,
    MergedItemsResponse,
    MergedModelTypeAdapter,
    RuleSetResponseTypeAdapter,
)
from mex.common.connector import HTTPConnector
from mex.common.models import (
    AnyExtractedModel,
    AnyMergedModel,
    AnyRuleSetRequest,
    AnyRuleSetResponse,
)
from mex.common.settings import BaseSettings


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

    def post_extracted_items(
        self,
        extracted_items: list[AnyExtractedModel],
    ) -> IdentifiersResponse:
        """Post extracted items to the backend in bulk.

        Args:
            extracted_items: Extracted items to post

        Raises:
            HTTPError: If post was not accepted, crashes or times out

        Returns:
            Response model from the endpoint
        """
        response = self.request(
            method="POST",
            endpoint="ingest",
            payload=ExtractedItemsRequest(items=extracted_items),
        )
        return IdentifiersResponse.model_validate(response)

    def fetch_extracted_items(
        self,
        query_string: str | None,
        stable_target_id: str | None,
        entity_type: list[str] | None,
        skip: int,
        limit: int,
    ) -> ExtractedItemsResponse:
        """Fetch extracted items that match the given set of filters.

        Args:
            query_string: Full-text search query
            stable_target_id: The item's stableTargetId
            entity_type: The item's entityType
            skip: How many items to skip for pagination
            limit: How many items to return in one page

        Raises:
            HTTPError: If search was not accepted, crashes or times out

        Returns:
            One page of extracted items and the total count that was matched
        """
        response = self.request(
            method="GET",
            endpoint="extracted-item",
            params={
                "q": query_string,
                "stableTargetId": stable_target_id,
                "entityType": entity_type,
                "skip": str(skip),
                "limit": str(limit),
            },
        )
        return ExtractedItemsResponse.model_validate(response)

    def fetch_merged_items(
        self,
        query_string: str | None,
        entity_type: list[str] | None,
        skip: int,
        limit: int,
    ) -> MergedItemsResponse:
        """Fetch merged items that match the given set of filters.

        Args:
            query_string: Full-text search query
            entity_type: The item's entityType
            skip: How many items to skip for pagination
            limit: How many items to return in one page

        Raises:
            HTTPError: If search was not accepted, crashes or times out

        Returns:
            One page of merged items and the total count that was matched
        """
        response = self.request(
            method="GET",
            endpoint="merged-item",
            params={
                "q": query_string,
                "entityType": entity_type,
                "skip": str(skip),
                "limit": str(limit),
            },
        )
        return MergedItemsResponse.model_validate(response)

    def get_merged_item(
        self,
        identifier: str,
    ) -> AnyMergedModel:
        """Return one merged item for the given `identifier`.

        Args:
            identifier: The merged item's identifier

        Raises:
            MExError: If no merged item was found

        Returns:
            A single merged item
        """
        # XXX stop-gap until the backend has a proper get merged item endpoint (MX-1669)
        response = self.request(
            method="GET",
            endpoint="merged-item",
            params={
                "identifier": identifier,
                "limit": "1",
            },
        )
        response_model = MergedItemsResponse.model_validate(response)
        try:
            return response_model.items[0]
        except IndexError:
            raise HTTPError("merged item was not found") from None

    def preview_merged_item(
        self,
        stable_target_id: str,
        rule_set: AnyRuleSetRequest,
    ) -> AnyMergedModel:
        """Return a preview for merging the given rule-set with stored extracted items.

        Args:
            stable_target_id: The extracted items' `stableTargetId`
            rule_set: A rule-set to use for previewing

        Raises:
            HTTPError: If preview produces errors, crashes or times out

        Returns:
            A single merged item
        """
        response = self.request(
            method="GET",
            endpoint=f"preview-item/{stable_target_id}",
            payload=rule_set,
        )
        return MergedModelTypeAdapter.validate_python(response)

    def get_rule_set(
        self,
        stable_target_id: str,
    ) -> AnyRuleSetResponse:
        """Return a triple of rules for the given `stableTargetId`.

        Args:
            stable_target_id: The merged item's identifier

        Raises:
            HTTPError: If no rule-set was found

        Returns:
            A set of three rules
        """
        response = self.request(
            method="GET",
            endpoint=f"rule-set/{stable_target_id}",
        )
        return RuleSetResponseTypeAdapter.validate_python(response)
