from typing import TYPE_CHECKING

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.decl_api import DeclarativeMeta

from mex.common.connector import BaseConnector
from mex.common.exceptions import MExError
from mex.common.settings import BaseSettings

if TYPE_CHECKING:  # pragma: no cover

    class Base(metaclass=DeclarativeMeta):
        """Type hint for declarative ORM base class."""

else:
    from mex.common.db.models import Base


class MexDBConnector(BaseConnector):
    """Connector class to handle mex db."""

    def __init__(self, settings: BaseSettings) -> None:
        """Create a new mex database connection.

        Args:
            settings: Configured settings instance
        """
        self.engine = create_engine(f"sqlite+pysqlite:///{settings.sqlite_path}")
        if not self._is_service_available():
            raise MExError(f"MEx database not available: {settings.sqlite_path}")
        Base.metadata.create_all(self.engine)

    def _is_service_available(self) -> bool:
        try:
            response = self.engine.execute("SELECT 1;")
            return bool(response.scalar_one())
        except SQLAlchemyError:
            return False

    def close(self) -> None:
        """Do nothing because no clean up is needed.

        We don't use ORM sessions yet, so nothing to do there. We also don't need to
        close connections or pools because with sqlite, they are closed immediately
        after query execution / cursor exhaustion.
        """
