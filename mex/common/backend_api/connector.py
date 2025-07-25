from collections.abc import Generator
from typing import Any, TypeVar
from urllib.parse import urljoin

from mex.common.connector import HTTPConnector
from mex.common.identity.models import Identity
from mex.common.models import (
    AnyExtractedModel,
    AnyMergedModel,
    AnyPreviewModel,
    AnyRuleSetRequest,
    AnyRuleSetResponse,
    ExtractedModelTypeAdapter,
    ExtractedOrganization,
    ExtractedPerson,
    ItemsContainer,
    MergedModelTypeAdapter,
    PaginatedItemsContainer,
    PreviewModelTypeAdapter,
    RuleSetResponseTypeAdapter,
)
from mex.common.settings import BaseSettings
from mex.common.types import Identifier, MergedPrimarySourceIdentifier

_IngestibleModelT = TypeVar(
    "_IngestibleModelT", bound=AnyExtractedModel | AnyRuleSetResponse
)


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

    def fetch_extracted_items(  # noqa: PLR0913
        self,
        *,
        query_string: str | None = None,
        stable_target_id: str | None = None,
        entity_type: list[str] | None = None,
        referenced_identifier: list[str] | None = None,
        reference_field: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> PaginatedItemsContainer[AnyExtractedModel]:
        """Fetch extracted items that match the given set of filters.

        Args:
            query_string: Full-text search query
            stable_target_id: The item's stableTargetId
            entity_type: The item's entityType
            referenced_identifier: Merged item identifiers filter
            reference_field: Field name to filter for
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
                "referencedIdentifier": referenced_identifier,
                "referenceField": reference_field,
                "skip": str(skip),
                "limit": str(limit),
            },
        )
        return PaginatedItemsContainer[AnyExtractedModel].model_validate(response)

    def get_extracted_item(
        self,
        identifier: str,
    ) -> AnyExtractedModel:
        """Return one extracted item for the given `identifier`.

        Args:
            identifier: The extracted item's identifier

        Raises:
            HTTPError: If no extracted item was found

        Returns:
            A single extracted item
        """
        response = self.request(
            method="GET",
            endpoint=f"extracted-item/{identifier}",
        )
        return ExtractedModelTypeAdapter.validate_python(response)

    def fetch_merged_items(  # noqa: PLR0913
        self,
        *,
        query_string: str | None = None,
        identifier: str | None = None,
        entity_type: list[str] | None = None,
        referenced_identifier: list[str] | None = None,
        reference_field: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> PaginatedItemsContainer[AnyMergedModel]:
        """Fetch merged items that match the given set of filters.

        Args:
            query_string: Full-text search query
            identifier: Merged item identifier filter
            entity_type: The items' entityType
            referenced_identifier: Merged item identifiers filter
            reference_field: Field name to filter for
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
                "identifier": identifier,
                "entityType": entity_type,
                "referencedIdentifier": referenced_identifier,
                "referenceField": reference_field,
                "skip": str(skip),
                "limit": str(limit),
            },
        )
        return PaginatedItemsContainer[AnyMergedModel].model_validate(response)

    def fetch_all_merged_items(
        self,
        *,
        query_string: str | None = None,
        identifier: str | None = None,
        entity_type: list[str] | None = None,
        referenced_identifier: list[str] | None = None,
        reference_field: str | None = None,
    ) -> Generator[AnyMergedModel, None, None]:
        """Fetch all merged items that match the given set of filters.

        Args:
            query_string: Full-text search query
            identifier: Merged item identifier filter
            entity_type: The items' entityType
            referenced_identifier: Merged item identifiers filter
            reference_field: Field name to filter for

        Raises:
            HTTPError: If search was not accepted, crashes or times out

        Returns:
            Generator for all merged items that match the filters
        """
        response = self.fetch_merged_items(
            query_string=query_string,
            identifier=identifier,
            entity_type=entity_type,
            referenced_identifier=referenced_identifier,
            reference_field=reference_field,
            skip=0,
            limit=1,
        )
        total_item_number = response.total
        item_number_limit = 100  # 100 is the maximum possible number per get-request
        for item_counter in range(0, total_item_number, item_number_limit):
            response = self.fetch_merged_items(
                query_string=query_string,
                identifier=identifier,
                entity_type=entity_type,
                referenced_identifier=referenced_identifier,
                reference_field=reference_field,
                skip=item_counter,
                limit=item_number_limit,
            )
            yield from response.items

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
        response = self.request(
            method="GET",
            endpoint=f"merged-item/{identifier}",
        )
        return MergedModelTypeAdapter.validate_python(response)

    def preview_merged_item(
        self,
        stable_target_id: str,
        rule_set: AnyRuleSetRequest,
    ) -> AnyPreviewModel:
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
        )
        return PreviewModelTypeAdapter.validate_python(response)

    def fetch_preview_items(  # noqa: PLR0913
        self,
        *,
        query_string: str | None = None,
        identifier: str | None = None,
        entity_type: list[str] | None = None,
        referenced_identifier: list[str] | None = None,
        reference_field: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> PaginatedItemsContainer[AnyPreviewModel]:
        """Fetch merged item previews that match the given set of filters.

        Args:
            query_string: Full-text search query
            identifier: Merged item identifier filter
            entity_type: The items' entityType
            referenced_identifier: Merged item identifiers filter
            reference_field: Field name to filter for
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
                "q": query_string,
                "identifier": identifier,
                "entityType": entity_type,
                "referencedIdentifier": referenced_identifier,
                "referenceField": reference_field,
                "skip": str(skip),
                "limit": str(limit),
            },
        )
        return PaginatedItemsContainer[AnyPreviewModel].model_validate(response)

    def create_rule_set(
        self,
        rule_set: AnyRuleSetRequest,
    ) -> AnyRuleSetResponse:
        """Create a new rule set.

        Args:
            rule_set: New rule-set to create

        Raises:
            HTTPError: If the rule-set did not validate

        Returns:
            The newly created rule-set
        """
        response = self.request(method="POST", endpoint="rule-set", payload=rule_set)
        return RuleSetResponseTypeAdapter.validate_python(response)

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

    def update_rule_set(
        self, stable_target_id: str, rule_set: AnyRuleSetRequest
    ) -> AnyRuleSetResponse:
        """Update an existing rule set.

        Args:
            stable_target_id: The merged item's identifier
            rule_set: The new rule-set contents

        Raises:
            HTTPError: If no rule-set was found

        Returns:
            A set of three rules
        """
        response = self.request(
            method="PUT", endpoint=f"rule-set/{stable_target_id}", payload=rule_set
        )
        return RuleSetResponseTypeAdapter.validate_python(response)

    def search_organization_in_wikidata(
        self,
        q: str,
        offset: int = 0,
        limit: int = 10,
    ) -> PaginatedItemsContainer[ExtractedOrganization]:
        """Search for organizations in wikidata.

        Args:
            q: Wikidata item ID or full URL
            offset: The starting index for pagination
            limit: The maximum number of results to return

        Returns:
            Paginated list of ExtractedOrganizations
        """
        response = self.request(
            method="GET",
            endpoint="wikidata",
            params={"q": q, "offset": str(offset), "limit": str(limit)},
        )
        return PaginatedItemsContainer[ExtractedOrganization].model_validate(response)

    def search_person_in_ldap(
        self,
        q: str,
        offset: int = 0,
        limit: int = 10,
    ) -> PaginatedItemsContainer[ExtractedPerson]:
        """Search for persons in LDAP.

        Args:
            q: The name of the person to be searched
            offset: The starting index for pagination
            limit: The maximum number of results to return

        Returns:
            Paginated list of ExtractedPersons
        """
        response = self.request(
            method="GET",
            endpoint="ldap",
            params={"q": q, "offset": str(offset), "limit": str(limit)},
        )
        return PaginatedItemsContainer[ExtractedPerson].model_validate(response)

    def search_person_in_orcid(
        self,
        q: str,
        offset: int = 0,
        limit: int = 10,
    ) -> PaginatedItemsContainer[ExtractedPerson]:
        """Search for persons in orcid.

        Args:
            q: The name of the person to be searched
            offset: The starting index for pagination
            limit: The maximum number of results to return

        Returns:
            Paginated list of ExtractedPersons
        """
        response = self.request(
            method="GET",
            endpoint="orcid",
            params={"q": q, "offset": str(offset), "limit": str(limit)},
        )
        return PaginatedItemsContainer[ExtractedPerson].model_validate(response)

    def assign_identity(
        self,
        had_primary_source: MergedPrimarySourceIdentifier,
        identifier_in_primary_source: str,
    ) -> Identity:
        """Find an Identity in a database or assign a new one."""
        response = self.request(
            "POST",
            "identity",
            {
                "hadPrimarySource": had_primary_source,
                "identifierInPrimarySource": identifier_in_primary_source,
            },
        )
        return Identity.model_validate(response)

    def fetch_identities(
        self,
        had_primary_source: Identifier | None = None,
        identifier_in_primary_source: str | None = None,
        stable_target_id: Identifier | None = None,
    ) -> ItemsContainer[Identity]:
        """Find Identity instances matching the given filters.

        Either provide `stableTargetId` or `hadPrimarySource`
        and `identifierInPrimarySource` together to get a unique result.
        """
        connector = BackendApiConnector.get()
        response = connector.request(
            "GET",
            "identity",
            params={
                "hadPrimarySource": had_primary_source,
                "identifierInPrimarySource": identifier_in_primary_source,
                "stableTargetId": stable_target_id,
            },
        )
        return ItemsContainer[Identity].model_validate(response)

    def ingest(
        self,
        ingestible_models: list[_IngestibleModelT],
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Post extracted models or rule-sets to the backend in bulk.

        Args:
            ingestible_models: Extracted models or rule-sets to ingest
            kwargs: Further keyword arguments passed to `requests`

        Raises:
            HTTPError: If post was not accepted, crashes or times out
        """
        self.request(
            method="POST",
            endpoint="ingest",
            payload=ItemsContainer[_IngestibleModelT](items=ingestible_models),
            **kwargs,
        )
