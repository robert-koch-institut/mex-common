from mex.common.cli import entrypoint
from mex.common.logging import echo
from mex.common.public_api.connector import PublicApiConnector
from mex.common.settings import BaseSettings


@entrypoint(BaseSettings)
def dump_api_authorization_header() -> None:  # pragma: no cover
    """Dump Public API authorization header to console."""
    connector = PublicApiConnector.get()
    settings = BaseSettings.get()
    echo(f"Authorization Header for {settings.public_api_url}:", fg="green")
    echo(connector.session.headers["Authorization"], fg="green")
