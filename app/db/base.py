
from sqlalchemy.orm import declarative_base

"""
Declarative base class for all SQLAlchemy ORM models.

This serves as the foundation for defining database models throughout
the application. Every model should inherit from this `Base` class
to automatically include SQLAlchemy's metadata and ORM mapping features.

Example:
    >>> from core.database import Base
    >>> class Article(Base):
    ...     __tablename__ = "articles"
    ...     id = Column(Integer, primary_key=True)
    ...     title = Column(String, nullable=False)

Returns:
    sqlalchemy.orm.decl_api.DeclarativeMeta: The base class used for ORM model declarations.
"""
Base = declarative_base()