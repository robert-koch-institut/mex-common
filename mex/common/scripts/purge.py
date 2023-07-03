from typing import cast

import click

from mex.common.cli import entrypoint
from mex.common.exceptions import MExError
from mex.common.logging import echo, get_ts
from mex.common.public_api.connector import PublicApiConnector
from mex.common.settings import BaseSettings
from mex.common.utils import jitter_sleep


@entrypoint(BaseSettings)
def purge() -> None:  # pragma: no cover
    """Purge all items from the Public API."""
    connector = PublicApiConnector.get()
    click.confirm(f"{get_ts()} really remove all items?", abort=True)

    offset_item_id = None
    item_ids = []
    for _ in range(1000):
        api_item_response = connector.get_all_items(offset_item_id=offset_item_id)
        offset_item_id = api_item_response.next
        item_ids.extend([item.itemId for item in api_item_response.items])
        if not offset_item_id:
            break
    else:
        raise MExError("Exceeded maximum fetchable amount of items.")
    chunks = [item_ids[i : i + 256] for i in range(0, len(item_ids), 256)]
    echo(f"got {len(item_ids)} items")

    for index, chunk in enumerate(chunks):
        echo(f"purge chunk {index + 1}/{len(chunks)}")
        connector.request("DELETE", "metadata/items", {"itemIds": chunk})
        jitter_sleep(0.1, 1)

    echo("clear old index", fg="red")
    response = connector.request("DELETE", "metadata/index")
    if job_id := cast(str, response.get("jobId")):
        connector.wait_for_job(job_id)

    echo("create new index", fg="green")
    response = connector.request("POST", "metadata/index")
    if job_id := cast(str, response.get("jobId")):
        connector.wait_for_job(job_id)
