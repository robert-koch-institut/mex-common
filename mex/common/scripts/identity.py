import pandas as pd
from pydantic import Field
from sqlalchemy import delete, insert, select

from mex.common.cli import entrypoint
from mex.common.identity.connector import IdentityConnector
from mex.common.identity.models import Identity
from mex.common.logging import echo
from mex.common.settings import BaseSettings
from mex.common.types import WorkPath


class IdentityScriptsSettings(BaseSettings):
    """Settings for identity-related scripts adding a csv-file parameter."""

    csv_file: WorkPath = Field(
        "identity.csv",
        description=(
            "Path to csv file containing identities, "
            "absolute path or relative to `work_dir`."
        ),
    )


@entrypoint(IdentityScriptsSettings)
def import_identities() -> None:
    """Load CSV file containing identities and overwrite local database.

    Settings:
        csv_file: Path to CSV file to load
    """
    settings = IdentityScriptsSettings.get()
    connector = IdentityConnector.get()

    df = pd.read_csv(
        settings.csv_file,
        usecols=[
            "platform_id",
            "original_id",
            "fragment_id",
            "merged_id",
            "entity_type",
            "annotation",
        ],
    )
    connector.engine.execute(delete(Identity))
    connector.engine.execute(insert(Identity).values(df.to_dict("records")))

    echo(f"[import identities] {len(df)} {settings.csv_file}", fg="green")


@entrypoint(IdentityScriptsSettings)
def export_identities() -> None:
    """Dump all identities in the local database to CSV format.

    Settings:
        csv_file: Path to CSV file to write
    """
    settings = IdentityScriptsSettings.get()
    connector = IdentityConnector.get()

    df = pd.read_sql(
        sql=select(Identity),
        con=connector.engine,
        index_col=Identity.merged_id.key,
    )
    df.to_csv(settings.csv_file, lineterminator="\n")

    echo(f"[export identitites] {len(df)} {settings.csv_file}", fg="green")
