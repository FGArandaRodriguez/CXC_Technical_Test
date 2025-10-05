from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

"""
Pydantic schemas for the Article model.

This module defines data validation, serialization, and automatic
OpenAPI documentation for the `Article` entity. It separates concerns
between input, update, and output representations to ensure data
integrity and clarity across API layers.

Classes:
    ArticleBase:
        Base schema defining shared attributes between all article operations.
    ArticleCreate:
        Schema used for article creation requests.
    ArticleUpdate:
        Schema used for partial updates of an existing article.
    ArticleInDB:
        Internal schema representing how an article is stored in the database,
        including metadata such as `id`, `created_at`, and `updated_at`.
    ArticleOut:
        Response schema used for returning article data to clients.
    ArticleList:
        Schema used for listing multiple articles.

"""


class ArticleBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    body: str = Field(..., min_length=10)
    author: str = Field(..., min_length=3, max_length=150)
    tags: Optional[List[str]] = Field(None, description="Lista de tags para el artículo")
    published_at: Optional[datetime] = None

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    body: Optional[str] = Field(None, min_length=10)
    tags: Optional[List[str]] = None
    published_at: Optional[datetime] = None

class ArticleInDB(ArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ArticleOut(ArticleInDB):
    pass

class ArticleList(BaseModel):
    articles: List[ArticleInDB]