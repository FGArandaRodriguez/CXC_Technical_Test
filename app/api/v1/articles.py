from fastapi import APIRouter, Depends, Query, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api import deps
from app.services.article_service import ArticleService
from app.repositories.article_repository import ArticleRepository
from app.schemas.article_schema import ArticleCreate, ArticleUpdate, ArticleOut

router = APIRouter()


@router.post("/", response_model=ArticleOut, status_code=status.HTTP_201_CREATED, summary="Create a new article")
def create_article(
    payload: ArticleCreate,
    db: Session = Depends(deps.get_db)
):
    """
    Create a new article.

    This endpoint:
      - Validates the input payload.
      - Ensures that the combination of `title` and `author` is unique.

    Args:
        payload (ArticleCreate): Article data for creation.
        db (Session): SQLAlchemy database session dependency.

    Returns:
        ArticleOut: The newly created article.
    """
    service = ArticleService(db)
    return service.create_article(payload)


@router.get("/{article_id}", response_model=ArticleOut, summary="Get an article by ID")
def get_article(
    article_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Retrieve a single article by its ID.

    This endpoint:
      - Fetches the article either from Redis cache or the database.
      - Improves performance using a cache-first strategy.

    Args:
        article_id (int): Unique identifier of the article.
        db (Session): SQLAlchemy database session dependency.

    Returns:
        ArticleOut: The requested article data.

    Raises:
        HTTPException: If the article does not exist.
    """
    service = ArticleService(db)
    return service.get_article(article_id)


@router.put("/{article_id}", response_model=ArticleOut, summary="Update an article")
def update_article(
    article_id: int,
    payload: ArticleUpdate,
    db: Session = Depends(deps.get_db)
):
    """
    Update an existing article by ID.

    This endpoint:
      - Updates article fields as provided in the payload.
      - Invalidates the Redis cache to prevent stale data.

    Args:
        article_id (int): Unique identifier of the article to update.
        payload (ArticleUpdate): Fields to be updated.
        db (Session): SQLAlchemy database session dependency.

    Returns:
        ArticleOut: The updated article data.

    Raises:
        HTTPException: If the article does not exist.
    """
    service = ArticleService(db)
    return service.update_article(article_id, payload)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an article")
def delete_article(
    article_id: int,
    db: Session = Depends(deps.get_db)
):
    """
    Delete an article by ID.

    This endpoint:
      - Removes the article from the database.
      - Invalidates the related cache entry in Redis.

    Args:
        article_id (int): Unique identifier of the article to delete.
        db (Session): SQLAlchemy database session dependency.

    Returns:
        Response: HTTP 204 No Content on successful deletion.

    Raises:
        HTTPException: If the article does not exist.
    """
    service = ArticleService(db)
    service.delete_article(article_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/", response_model=List[ArticleOut], summary="List all articles")
def list_articles(
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    author: Optional[str] = Query(None, description="Filter by author"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """
    Retrieve a paginated list of articles with filtering and sorting options.

    This endpoint provides:
      - **Pagination** via `skip` and `limit`.
      - **Filtering** by `tag` and `author`.
      - **Sorting** by `published_at` in ascending or descending order.

    Args:
        db (Session): SQLAlchemy database session dependency.
        skip (int): Number of records to skip (default: 0).
        limit (int): Maximum number of records to return (default: 20).
        tag (Optional[str]): Filter results by tag.
        author (Optional[str]): Filter results by author name.
        sort_order (str): Sorting order, either "asc" or "desc".

    Returns:
        List[ArticleOut]: A list of article objects.
    """
    repo = ArticleRepository()
    articles, _ = repo.list(
        db, skip=skip, limit=limit, tag=tag, author=author, sort_order=sort_order
    )
    return articles
