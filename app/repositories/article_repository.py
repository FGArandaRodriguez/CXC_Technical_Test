from sqlalchemy.orm import Session
from app.db.models import Article
from app.schemas.article_schema import ArticleCreate, ArticleUpdate
from typing import List, Optional, Tuple

class ArticleRepository:
    """
    Data access layer (Repository) for the Article model.

    This module encapsulates all database operations related to the `Article` entity,
    providing a clean and reusable interface for CRUD operations and advanced queries.

    Responsibilities:
        - Retrieve, list, create, update, and delete articles.
        - Handle query filtering, pagination, and sorting.
        - Convert tag lists into a semicolon-separated string for storage.
        - Maintain database session integrity (commit, rollback, refresh).

    Classes:
        ArticleRepository:
            Provides methods for interacting with the Article table using SQLAlchemy ORM.
            Each method isolates persistence logic to ensure clean separation from 
            business and presentation layers.

    """
    
    model = Article
    def _tags_to_string(self, tags: Optional[List[str]]) -> Optional[str]:
        return ";".join(tags) if tags else None

    def get(self, db: Session, article_id: int) -> Optional[Article]:
        return db.query(Article).filter(Article.id == article_id).first()

    def get_by_title_and_author(self, db: Session, title: str, author: str) -> Optional[Article]:
        return db.query(Article).filter(Article.title == title, Article.author == author).first()

    def list(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        tag: Optional[str] = None,
        author: Optional[str] = None,
        search: Optional[str] = None,
        sort_order: str = "desc"
    ) -> Tuple[List[Article], int]:
        """Lista artículos con filtros, paginación, búsqueda opcional y ordenamiento."""
        
        # --- AÑADE ESTA LÍNEA DE DEPURACIÓN ---
        print(f"🔍 Repositorio recibió el parámetro de búsqueda: '{search}'")

        query = db.query(Article)

        if author:
            query = query.filter(Article.author == author)
        if tag:
            query = query.filter(Article.tags.ilike(f"%{tag}%"))
        
        if search:
            print("✅ Aplicando filtro de búsqueda...")
            search_query = f"%{search}%"
            query = query.filter(
                (Article.title.ilike(search_query)) | (Article.body.ilike(search_query))
            )

        # --- AÑADE ESTAS LÍNEAS PARA VER EL SQL ---
        # Compila y muestra la consulta SQL exacta que se va a ejecutar
        compiled_query = query.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
        print("--- 📜 SQL Generado ---")
        print(compiled_query)
        print("----------------------")

        order_column = Article.published_at
        if sort_order == "asc":
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc().nullslast())

        total = query.count()
        articles = query.offset(skip).limit(limit).all()
        return articles, total

    def create(self, db: Session, payload: ArticleCreate) -> Article:
        db_article = Article(
            title=payload.title,
            body=payload.body,
            author=payload.author,
            tags=self._tags_to_string(payload.tags),
            published_at=payload.published_at
        )
        db.add(db_article)
        db.commit()
        db.refresh(db_article)
        return db_article

    def update(self, db: Session, db_obj: Article, payload: ArticleUpdate) -> Article:
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "tags":
                setattr(db_obj, field, self._tags_to_string(value))
            else:
                setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: Article) -> Article:
        db.delete(db_obj)
        db.commit()
        return db_obj