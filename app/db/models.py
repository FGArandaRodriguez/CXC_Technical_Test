from sqlalchemy import Column, Integer, String, Text, DateTime, func, UniqueConstraint, Index, text
from app.db.base import Base
from datetime import datetime

class Article(Base):
    
    """
    Database model for the `articles` table.
    
    Represents a published or draft article within the system, including metadata
    such as author, publication date, and timestamps for creation and updates.
    
    Attributes:
        id (int): Primary key identifier for the article.
        title (str): Title of the article. Cannot be null.
        author (str): Author's name. Cannot be null.
        body (str): Full text content of the article.
        tags (str | None): Optional tags separated by semicolons (';').
        published_at (datetime | None): Timestamp when the article was published.
        created_at (datetime): Timestamp automatically set when the record is created.
        updated_at (datetime): Timestamp automatically updated on modification.
    
    Table Args:
        UniqueConstraint('title', 'author', name='uix_title_author'): 
            Ensures that the same author cannot publish multiple articles 
            with the same title.
        Index('ix_articles_author', 'author'): 
            Improves query performance for lookups by author.
        Index('ix_articles_published_at', 'published_at'): 
            Optimizes filtering and sorting by publication date.
    """
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(150), nullable=False)
    body = Column(Text, nullable=False)
    tags = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    __table_args__ = (
        UniqueConstraint("title", "author", name="uix_title_author"),
        Index("ix_articles_author", "author"),
        Index("ix_articles_published_at", "published_at"),
    )