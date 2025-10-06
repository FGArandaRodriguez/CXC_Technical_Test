from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.article_repository import ArticleRepository
from app.schemas.article_schema import ArticleCreate, ArticleUpdate, ArticleOut
from app.cache.redis_wrapper import CacheWrapper

class ArticleService:
    """
    Business logic layer for managing Article entities.

    This module coordinates the workflow between the database repository (data layer)
    and the Redis cache (infrastructure layer). It defines high-level operations that 
    encapsulate validation, caching strategy, and exception handling for the `Article` domain.

    Responsibilities:
        - Retrieve articles, prioritizing cached data when available.
        - Create new articles while enforcing uniqueness constraints.
        - Update or delete existing articles and invalidate corresponding cache entries.
        - Translate low-level repository results into Pydantic response models (ArticleOut).

    Classes:
        ArticleService:
            Provides business logic methods for interacting with articles, integrating
            the repository (persistence layer) and cache wrapper (Redis layer).
            
    """
    def __init__(self, db: Session):
        self.db = db
        self.repo = ArticleRepository()
        self.cache = CacheWrapper()
        

    def get_article(self, article_id: int) -> ArticleOut:
        cached_article = self.cache.get(article_id)
        if cached_article:
            return ArticleOut.model_validate(cached_article)

        db_article = self.repo.get(self.db, article_id)
        if not db_article:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        
        article_out = ArticleOut.from_orm(db_article)
        self.cache.set(article_id, article_out.model_dump())
        return article_out

    def create_article(self, payload: ArticleCreate) -> ArticleOut:
        existing_article = self.repo.get_by_title_and_author(self.db, title=payload.title, author=payload.author)
        if existing_article:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An article with the same title and author already exists."
            )
        db_article = self.repo.create(self.db, payload=payload)
        return ArticleOut.from_orm(db_article)

    def update_article(self, article_id: int, payload: ArticleUpdate) -> ArticleOut:
        db_article = self.repo.get(self.db, article_id)
        if not db_article:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

        updated_article = self.repo.update(self.db, db_obj=db_article, payload=payload)
        self.cache.invalidate(article_id)
        return ArticleOut.from_orm(updated_article)

    def delete_article(self, article_id: int):
        db_article = self.repo.get(self.db, article_id)
        if not db_article:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

        self.repo.delete(self.db, db_obj=db_article)
        self.cache.invalidate(article_id)
        return
    