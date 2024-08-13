from typing import cast
from urllib.parse import urljoin

from mex.common.backend_api.models import (
    ExtractedItemsRequest,
    ExtractedItemsResponse,
    IdentifiersResponse,
    MergedItemsResponse,
    MergedModelTypeAdapter,
    RuleSetResponseTypeAdapter,
)
from mex.common.connector import HTTPConnector
from mex.common.exceptions import MExError
from mex.common.models import (
    AnyExtractedModel,
    AnyMergedModel,
    AnyRuleSetRequest,
    AnyRuleSetResponse,
)
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
        self,
        extracted_items: list[AnyExtractedModel],
    ) -> list[AnyExtractedIdentifier]:
        """Post extracted models to the backend in bulk.

        Args:
            extracted_items: Extracted models to post

        Raises:
            HTTPError: If post was not accepted, crashes or times out

        Returns:
            Identifiers of posted extracted models
        """
        # XXX deprecated method, please use `post_extracted_models` instead
        return cast(
            list[AnyExtractedIdentifier],
            self.post_extracted_items(extracted_items).identifiers,
        )

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

    def fetch_merged_models(
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

        Returns:
            One page of merged items and the total count that was matched
        """
        # XXX this endpoint will only return faux merged items for now (MX-1382)
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

    def get_merged_model(
        self,
        stable_target_id: str,
    ) -> AnyMergedModel:
        """Return one merged item for the given `stableTargetId`.

        Args:
            stable_target_id: The merged item's identifier

        Returns:
            A single merged item
        """
        # XXX stop-gap until the backend has a proper get merged item endpoint (MX-1669)
        response = self.request(
            method="GET",
            endpoint="merged-item",
            params={
                "stableTargetId": stable_target_id,
                "limit": "1",
            },
        )
        response_model = MergedItemsResponse.model_validate(response)
        try:
            return response_model.items[0]
        except IndexError:
            raise MExError("merged item was not found") from None

    def preview_merged_model(
        self,
        stable_target_id: str,
        rule_set: AnyRuleSetRequest,
    ) -> AnyMergedModel:
        """Return a preview for merging the given rule-set with stored extracted items.

        Args:
            stable_target_id: The extracted items' `stableTargetId`
            rule_set: A rule-set to use for previewing

        Returns:
            A single merged item
        """
        # XXX experimental method until the backend has a preview endpoint (MX-1406)
        response = self.request(
            method="GET", endpoint=f"preview-item/{stable_target_id}", payload=rule_set
        )
        return MergedModelTypeAdapter.validate_python(response)

    def get_rule_set(
        self,
        stable_target_id: str,
    ) -> AnyRuleSetResponse:
        """Return a triple of rules for the given `stableTargetId`.

        Args:
            stable_target_id: The merged item's identifier

        Returns:
            A set of three rules
        """
        # XXX experimental method until the backend has a rule-set endpoint (MX-1416)
        response = self.request(
            method="GET",
            endpoint=f"rule-set/{stable_target_id}",
        )
        return RuleSetResponseTypeAdapter.validate_python(response)
