import json
from base64 import b64decode
from datetime import datetime, timedelta
from typing import Final, Generator, TypeVar, cast
from urllib.parse import urljoin
from uuid import UUID

import backoff
import pandas as pd
import requests
from requests.exceptions import HTTPError

from mex.common.connector import HTTPConnector
from mex.common.logging import echo
from mex.common.models import MExModel
from mex.common.public_api.models import (
    PublicApiAuthResponse,
    PublicApiAxisConstraint,
    PublicApiItem,
    PublicApiItemWithoutValues,
    PublicApiJobItemsResponse,
    PublicApiMetadataItemsResponse,
    PublicApiSearchRequest,
    PublicApiSearchResponse,
)
from mex.common.public_api.transform import (
    transform_mex_model_to_public_api_item,
    transform_public_api_item_to_mex_model,
)
from mex.common.settings import BaseSettings
from mex.common.types import Identifier

ModelT = TypeVar("ModelT", bound=MExModel)
PublicApiItemT = TypeVar(
    "PublicApiItemT", bound=PublicApiItem | PublicApiItemWithoutValues
)


class PublicApiConnector(HTTPConnector):  # pragma: no cover
    """Connector class to handle authentication and interaction with the public API."""

    API_VERSION: Final[str] = "v0"

    def _set_session(self) -> None:
        """Create and set request session."""
        settings = BaseSettings.get()
        self.session = requests.Session()
        self.session.verify = settings.public_api_verify_session  # type: ignore

    def _set_url(self) -> None:
        """Set url of the host with api version."""
        settings = BaseSettings.get()
        self.url = urljoin(str(settings.public_api_url), self.API_VERSION)

    def _check_availability(self) -> None:
        """Send an empty search request to verify the host is available."""
        self.request(
            "POST",
            "/query/search",
            PublicApiSearchRequest(limit=0),
        )

    def _set_authentication(self) -> None:
        """Generate JWT using secret payload and attach it to session."""
        settings = BaseSettings.get()
        response = self.session.post(
            str(settings.public_api_token_provider),
            data=b64decode(settings.public_api_token_payload.get_secret_value()),
            timeout=self.TIMEOUT,
            headers={"Accept": "*/*", "Authorization": None},
        )
        response.raise_for_status()
        auth_response = PublicApiAuthResponse.model_validate(response.json())
        expires_at = datetime.now() + timedelta(seconds=auth_response.expires_in)
        echo(
            f"authenticated with public api (expires {expires_at})", fg="bright_magenta"
        )
        self.session.headers["Authorization"] = f"Bearer {auth_response.access_token}"

    def echo_job_logs(self, job_id: str) -> None:
        """Echo the logs for the job with the given ID to the console.

        Args:
            job_id: Public API job ID
        """
        response = self.request("GET", f"jobs/{job_id}/logs")
        raw_logs = cast(list[str], response.get("logs"))
        now = str(datetime.now())
        for raw_log in raw_logs:
            log = json.loads(raw_log)
            if trace := log.get("trace-id"):
                timestamp = pd.to_datetime(log.get("timestamp", now))
                message = f"[{trace}] {log.get('message', 'N/A')}"
                echo(message, timestamp, fg="bright_magenta")

    @backoff.on_predicate(
        backoff.fibo, lambda status: cast(str, status) == "RUNNING", max_time=180
    )
    def wait_for_job(self, job_id: str) -> str:
        """Poll the status for this `job_id` until it is no longer 'RUNNING'."""
        response = self.request("GET", f"jobs/{job_id}")
        return str(response.get("status", "NONE"))

    def get_job_items(self, job_id: str) -> Generator[Identifier, None, None]:
        """Get the identifiers of the items created, updated or deleted during a job.

        Args:
            job_id: Job to query for items

        Returns:
            Generator for identifiers of manipulated items
        """
        response = self.request("GET", f"jobs/{job_id}/items")
        items_response = PublicApiJobItemsResponse.model_validate(response)
        for item_id in items_response.itemIds:
            if isinstance(item_id, UUID):
                if item := self.get_item(item_id):
                    for field in item.values:
                        if field.fieldName == "identifier":
                            yield Identifier(field.fieldValue)

    def post_items(
        self, items: list[PublicApiItem], wait_for_done: bool = True
    ) -> list[Identifier]:
        """Post a list of items them to the public API.

        Args:
            items: Public API items to post
            wait_for_done: If the return should block until the job is done

        Raises:
            HTTPError: If the job was not accepted, crashes or times out

        Returns:
            Identifiers of created or updated models
            Empty list in case `wait_for_done` was `False`
        """
        response = self.request("POST", "metadata/items_bulk", {"items": items})
        job_id = response.get("jobId", "N/A")
        if wait_for_done:
            self.wait_for_job(job_id)
            return list(self.get_job_items(job_id))
        return []

    def post_models(
        self, models: list[MExModel], wait_for_done: bool = True
    ) -> list[Identifier]:
        """Convert models to public API items and post them.

        Args:
            models: Extracted or merged models to post
            wait_for_done: If the return should block until the job is done

        Raises:
            HTTPError: If the job was not accepted, crashes or times out

        Returns:
            Identifiers of created or updated items
            Empty list in case `wait_for_done` was `False`
        """
        return self.post_items(
            [transform_mex_model_to_public_api_item(model) for model in models],
            wait_for_done=wait_for_done,
        )

    def search_item(
        self, model_cls: type[ModelT], identifier: Identifier
    ) -> PublicApiItem | None:
        """Search an item and retrieve it from public API.

        Uses the search endpoint of the public API, which covers only a subset of
        (e.g. no persons or primary sources)

        Args:
            model_cls: Class of the expected model
            identifier: Identifier of the model

        Returns:
            Public API item, if ID was found, else None
        """
        request = PublicApiSearchRequest(
            offset=0,
            limit=1,
            axisConstraints=[
                PublicApiAxisConstraint(values=[str(identifier)], axis="identifier"),
                PublicApiAxisConstraint(values=[model_cls.__name__], axis="entityName"),
            ],
            fields=list(model_cls.model_fields),
        )
        response = self.request(
            "POST",
            "query/search",
            request,
        )
        search_response = PublicApiSearchResponse.model_validate(response)
        if search_response.numFound == 1 and len(search_response.items) == 1:
            return search_response.items[0]
        return None

    def get_item(self, identifier: Identifier | UUID) -> PublicApiItem | None:
        """Get an item from Public API.

        Args:
            identifier: Identifier of the Public API item

        Returns:
            Public API item, if ID was found, else None
        """
        try:
            response = self.request("GET", f"metadata/items/{identifier}")
        except HTTPError as error:
            # no rows in result set, return None
            if error.response and error.response.status_code == 404:
                return None
            # re-raise any unexpected errors
            raise error
        else:
            return PublicApiItem.model_validate(response)

    def search_model(
        self, model_cls: type[ModelT], identifier: Identifier
    ) -> MExModel | None:
        """Get an item from the Public API and convert it to a model.

        Args:
            model_cls: Class of the expected model
            identifier: Identifier of the model

        Returns:
            Extracted or merged model instance, if ID was found, else None
        """
        if item := self.search_item(model_cls, identifier):
            return transform_public_api_item_to_mex_model(item)
        return None

    def delete_item(
        self, item: PublicApiItem | PublicApiItemWithoutValues
    ) -> UUID | None:
        """Delete item from Public API.

        Args:
            item: Public API item to delete

        Raises:
            HTTPError: If deletion failed

        Returns:
            API-internal UUID of the deleted item, or None if item had no ID
        """
        if item.itemId:
            self.request(
                "DELETE",
                f"metadata/items/{item.itemId}",
            )
            return item.itemId
        return None

    def delete_model(self, model: MExModel) -> UUID | None:
        """Get the Public API item for a given model and delete it.

        Requires that the model is findable via the Public API, which is not true for
        Persons among other model types

        Args:
            model: MEx model instance

        Raises:
            HTTPError: If deletion failed

        Returns:
            API-internal UUID of the deleted item, or None if model did not exist
        """
        if item := self.search_item(type(model), model.identifier):
            return self.delete_item(item)
        return None

    def search_items(
        self,
        model_cls: type[MExModel],
        offset: int = 0,
        limit: int = 10,
    ) -> list[PublicApiItem]:
        """Get all Public API items corresponding to `model_cls` with pagination.

        Uses the search endpoint of the Public API,
        which covers only a subset of entities (e.g. no persons or primary sources)

        Args:
            model_cls: Model class to fetch
            offset: Pagination offset, defaults to 0
            limit: Pagination limit, defaults to 10

        Returns:
            List of Public API items
        """
        request = PublicApiSearchRequest(
            offset=offset,
            limit=limit,
            axisConstraints=[
                PublicApiAxisConstraint(values=[model_cls.__name__], axis="entityName")
            ],
            fields=list(model_cls.model_fields),
        )
        response = self.request(
            "POST",
            "query/search",
            request,
        )
        return PublicApiSearchResponse.model_validate(response).items

    def search_mex_model_items(
        self, model_cls: type[ModelT], offset: int = 0, limit: int = 10
    ) -> list[ModelT]:
        """Get all instances of a model class with pagination.

        Args:
            model_cls: Model class to fetch
            offset: Pagination offset, defaults to 0
            limit: Pagination limit, defaults to 10

        Returns:
            List of instances of `model_cls`
        """
        return [
            model
            for item in self.search_items(model_cls, offset, limit)
            if (model := cast(ModelT, transform_public_api_item_to_mex_model(item)))
        ]

    def get_all_items(
        self, offset_item_id: UUID | None = None
    ) -> PublicApiMetadataItemsResponse:
        """Get all items from the Public API endpoint 'metadata/items'.

        Args:
            offset_item_id: item UUID pagination offset, defaults to None
        """
        endpoint = "metadata/items"
        if offset_item_id:
            endpoint += f"?next={offset_item_id}"
        response = self.request("GET", endpoint)
        return PublicApiMetadataItemsResponse.model_validate(response)
