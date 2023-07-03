from typing import TYPE_CHECKING

from pydantic import NoneStr
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm.decl_api import DeclarativeMeta

from mex.common.models.base import BaseModel

if TYPE_CHECKING:  # pragma: no cover

    class Base(metaclass=DeclarativeMeta):
        """Type hint for declarative ORM base class."""

else:
    from mex.common.db.models import Base


class SeedPrimarySource(BaseModel):
    """Model class for primary sources coming from the JSON seed file."""

    identifier: str
    alternative_title: list[str] = []
    contact: list[str] = []
    description: list[str] = []
    documentation: list[str] = []
    located_at: list[str]
    title: list[str] = []
    unit_in_charge: list[str]
    version: NoneStr = None


class MExDBPrimarySource(Base):
    """SQLAlchemy model for the primary source."""

    __tablename__ = "primary_sources"

    if TYPE_CHECKING:  # pragma: no cover
        identifier: str
        alternative_titles: list["AlternativeTitle"]
        contacts: list["Contact"]
        descriptions: list["Description"]
        documentations: list["Documentation"]
        located_ats: list["LocatedAt"]
        titles: list["Title"]
        units_in_charge: list["UnitInCharge"]
        version: str

    else:
        identifier = Column(Text(64), primary_key=True)
        version = Column(Text(256), nullable=True)

        alternative_titles = relationship(
            "AlternativeTitle", back_populates="primary_source"
        )
        contacts = relationship("Contact", back_populates="primary_source")
        descriptions = relationship("Description", back_populates="primary_source")
        documentations = relationship("Documentation", back_populates="primary_source")
        located_ats = relationship("LocatedAt", back_populates="primary_source")
        titles = relationship("Title", back_populates="primary_source")
        units_in_charge = relationship("UnitInCharge", back_populates="primary_source")


class AlternativeTitle(Base):
    """SQLAlchemy model for primary source alternative titles."""

    __tablename__ = "alternative_titles"

    if TYPE_CHECKING:  # pragma: no cover
        alternative_title_id: str
        alternative_title: str
        primary_source_id: int
        primary_source: MExDBPrimarySource
    else:
        alternative_title_id = Column(Integer, primary_key=True, autoincrement=True)
        alternative_title = Column(Text(2000), nullable=True)
        primary_source_id = Column(Text(64), ForeignKey("primary_sources.identifier"))

        primary_source = relationship(
            "MExDBPrimarySource", back_populates="alternative_titles"
        )


class Contact(Base):
    """SQLAlchemy model for primary source contacts."""

    __tablename__ = "contacts"

    if TYPE_CHECKING:  # pragma: no cover
        contact_id: int
        identifier: str
        contact: str
        primary_source_id: int
        primary_source: MExDBPrimarySource
    else:
        contact_id = Column(Integer, primary_key=True, autoincrement=True)
        contact = Column(Text(200), nullable=True, unique=False)
        primary_source_id = Column(Text(64), ForeignKey("primary_sources.identifier"))

        primary_source = relationship("MExDBPrimarySource", back_populates="contacts")


class Description(Base):
    """SQLAlchemy model for primary source descriptions."""

    __tablename__ = "descriptions"

    if TYPE_CHECKING:  # pragma: no cover
        description_id: str
        description: str
        primary_source_id: int
        primary_source: MExDBPrimarySource

    else:
        description_id = Column(Integer, primary_key=True, autoincrement=True)
        description = Column(Text(2048), nullable=True)
        primary_source_id = Column(Text(64), ForeignKey("primary_sources.identifier"))

        primary_source = relationship(
            "MExDBPrimarySource", back_populates="descriptions"
        )


class Documentation(Base):
    """SQLAlchemy model for primary source documentations."""

    __tablename__ = "documentations"

    if TYPE_CHECKING:  # pragma: no cover
        documentation_id: str
        documentation: str
        primary_source_id: int
        primary_source: MExDBPrimarySource

    else:
        documentation_id = Column(Integer, primary_key=True, autoincrement=True)
        documentation = Column(Text(2048), nullable=True)
        primary_source_id = Column(Text(64), ForeignKey("primary_sources.identifier"))

        primary_source = relationship(
            "MExDBPrimarySource", back_populates="documentations"
        )


class LocatedAt(Base):
    """SQLAlchemy model for primary source located at info."""

    __tablename__ = "located_ats"

    if TYPE_CHECKING:  # pragma: no cover
        located_at_id: str
        located_at: str
        primary_source_id: int
        primary_source: MExDBPrimarySource

    else:
        located_at_id = Column(Integer, primary_key=True, autoincrement=True)
        located_at = Column(Text(2048), nullable=True)
        primary_source_id = Column(Text(64), ForeignKey("primary_sources.identifier"))

        primary_source = relationship(
            "MExDBPrimarySource", back_populates="located_ats"
        )


class Title(Base):
    """SQLAlchemy model for primary source titles."""

    __tablename__ = "titles"

    if TYPE_CHECKING:  # pragma: no cover
        title_id: int
        title: str
        primary_source_id: str
        primary_source: MExDBPrimarySource
    else:
        title_id = Column(Integer, primary_key=True, autoincrement=True)
        title = Column(Text(1024), nullable=True)
        primary_source_id = Column(Text(64), ForeignKey("primary_sources.identifier"))

        primary_source = relationship("MExDBPrimarySource", back_populates="titles")


class UnitInCharge(Base):
    """SQLAlchemy model for primary source units in charge."""

    __tablename__ = "units_in_charge"

    if TYPE_CHECKING:  # pragma: no cover
        unit_in_charge_id: int
        unit_in_charge: str
        primary_source_id: str
        primary_source: MExDBPrimarySource
    else:
        unit_in_charge_id = Column(Integer, primary_key=True, autoincrement=True)
        unit_in_charge = Column(Text(1024), nullable=True)
        primary_source_id = Column(Text(64), ForeignKey("primary_sources.identifier"))

        primary_source = relationship(
            "MExDBPrimarySource", back_populates="units_in_charge"
        )
