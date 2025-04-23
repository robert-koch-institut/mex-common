from urllib.parse import urljoin

from requests.exceptions import HTTPError

from mex.common.backend_api.models import (
    MergedModelTypeAdapter,
    RuleSetResponseTypeAdapter,
)
from mex.common.connector import HTTPConnector
from mex.common.models import (
    AnyExtractedModel,
    AnyMergedModel,
    AnyPreviewModel,
    AnyRuleSetRequest,
    AnyRuleSetResponse,
    ItemsContainer,
    PaginatedItemsContainer,
)
from mex.common.settings import BaseSettings


class BackendApiConnector(HTTPConnector):
    """Connector class to handle interaction with the Backend API."""

    API_VERSION = "v0"
    INGEST_TIMEOUT = 30

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

    def ingest(
        self,
        models_or_rule_sets: list[AnyExtractedModel | AnyRuleSetResponse],
    ) -> list[AnyExtractedModel | AnyRuleSetResponse]:
        """Post extracted models or rule-sets to the backend in bulk.

        Args:
            models_or_rule_sets: Extracted models or rule-sets to ingest

        Raises:
            HTTPError: If post was not accepted, crashes or times out

        Returns:
            List of extracted models or rule-sets from the endpoint
        """
        response = self.request(
            method="POST",
            endpoint="ingest",
            payload=ItemsContainer[AnyExtractedModel | AnyRuleSetResponse](
                items=models_or_rule_sets
            ),
            params={
                "format": "json",
            },
            timeout=self.INGEST_TIMEOUT,
        )
        return (
            ItemsContainer[AnyExtractedModel | AnyRuleSetResponse]
            .model_validate(response)
            .items
        )

    def fetch_extracted_items(
        self,
        query_string: str | None,
        stable_target_id: str | None,
        entity_type: list[str] | None,
        skip: int,
        limit: int,
    ) -> PaginatedItemsContainer[AnyExtractedModel]:
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
                "format": "json",
                "q": query_string,
                "stableTargetId": stable_target_id,
                "entityType": entity_type,
                "skip": str(skip),
                "limit": str(limit),
            },
        )
        return PaginatedItemsContainer[AnyExtractedModel].model_validate(response)

    def fetch_merged_items(
        self,
        query_string: str | None,
        entity_type: list[str] | None,
        had_primary_source: list[str] | None,
        skip: int,
        limit: int,
    ) -> PaginatedItemsContainer[AnyMergedModel]:
        """Fetch merged items that match the given set of filters.

        Args:
            query_string: Full-text search query
            entity_type: The items' entityType
            had_primary_source: The items' hadPrimarySource
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
                "format": "json",
                "q": query_string,
                "entityType": entity_type,
                "hadPrimarySource": had_primary_source,
                "skip": str(skip),
                "limit": str(limit),
            },
        )
        return PaginatedItemsContainer[AnyMergedModel].model_validate(response)

    def get_merged_item(
        self,
        identifier: str,
    ) -> AnyMergedModel:
        """Return one merged item for the given `identifier`.

        Args:
            identifier: The merged item's identifier

        Raises:
            HTTPError: If no merged item was found

        Returns:
            A single merged item
        """
        # TODO(ND): stop-gap until backend has proper get merged item endpoint (MX-1669)
        response = self.request(
            method="GET",
            endpoint="merged-item",
            params={
                "format": "json",
                "identifier": identifier,
                "limit": "1",
            },
        )
        response_model = PaginatedItemsContainer[AnyMergedModel].model_validate(
            response
        )
        try:
            return response_model.items[0]
        except IndexError:
            msg = "merged item was not found"
            raise HTTPError(msg) from None

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
            method="POST",
            endpoint=f"preview-item/{stable_target_id}",
            payload=rule_set,
            params={
                "format": "json",
            },
        )
        return MergedModelTypeAdapter.validate_python(response)

    def fetch_preview_items(
        self,
        query_string: str | None,
        entity_type: list[str] | None,
        had_primary_source: list[str] | None,
        skip: int,
        limit: int,
    ) -> PaginatedItemsContainer[AnyPreviewModel]:
        """Fetch merged item previews that match the given set of filters.

        Args:
            query_string: Full-text search query
            entity_type: The items' entityType
            had_primary_source: The items' hadPrimarySource
            skip: How many items to skip for pagination
            limit: How many items to return in one page

        Raises:
            HTTPError: If search was not accepted, crashes or times out

        Returns:
            One page of preview items and the total count that was matched
        """
        response = self.request(
            method="GET",
            endpoint="preview-item",
            params={
                "format": "json",
                "q": query_string,
                "entityType": entity_type,
                "hadPrimarySource": had_primary_source,
                "skip": str(skip),
                "limit": str(limit),
            },
        )
        return PaginatedItemsContainer[AnyPreviewModel].model_validate(response)

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
            params={
                "format": "json",
            },
        )
        return RuleSetResponseTypeAdapter.validate_python(response)
