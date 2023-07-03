from typing import cast

from mex.common.cli import entrypoint
from mex.common.logging import echo
from mex.common.public_api.connector import PublicApiConnector
from mex.common.settings import BaseSettings


@entrypoint(BaseSettings)
def refresh() -> None:  # pragma: no cover
    """Refresh the search index in the Public API."""
    connector = PublicApiConnector.get()

    echo("refreshing index", fg="green")
    response = connector.request("PUT", "metadata/index")
    if job_id := cast(str, response.get("jobId")):
        connector.wait_for_job(job_id)
