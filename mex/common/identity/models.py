from typing import TYPE_CHECKING

from sqlalchemy import Column, Text, UniqueConstraint
from sqlalchemy.orm.decl_api import DeclarativeMeta

if TYPE_CHECKING:  # pragma: no cover

    class Base(metaclass=DeclarativeMeta):
        """Type hint for declarative ORM base class."""

else:
    from mex.common.db.models import Base


class Identity(Base):
    """SQLAlchemy model for the identifier lookup database."""

    __tablename__ = "identity"
    __table_args__ = (UniqueConstraint("platform_id", "original_id"),)
    fragment_id = Column(Text(36), primary_key=True)  # identifier
    platform_id = Column(Text(36), nullable=False)  # had_primary_source
    original_id = Column(Text(256), nullable=False)  # identifier_in_primary_source
    merged_id = Column(Text(36), nullable=False)  # stable_target_id
    entity_type = Column(Text(32), nullable=False)  # get_entity_type()
    annotation = Column(Text(4048), nullable=False)  # deprecated
