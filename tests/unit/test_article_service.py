import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.services.article_service import ArticleService
from app.schemas.article_schema import ArticleCreate
from datetime import datetime

def test_get_article_cache_hit():
    """
    PRUEBA UNITARIA: Verifica que si un artículo está en el caché,
    el servicio lo devuelve sin consultar la base de datos.
    """
    mock_db = MagicMock()
    
    with patch('app.services.article_service.CacheWrapper') as MockCache, \
         patch('app.services.article_service.ArticleRepository') as MockRepo:
        
        mock_cache_instance = MockCache.return_value
        # CORRECCIÓN: 'body' ahora es válido.
        cached_article_data = {
            "id": 1, "title": "Cached Title", "body": "This is a valid body.", "author": "Author", 
            "tags": ["test"], "published_at": None, 
            "created_at": "2025-01-01T12:00:00", "updated_at": "2025-01-01T12:00:00"
        }
        mock_cache_instance.get.return_value = cached_article_data
        
        mock_repo_instance = MockRepo.return_value
        service = ArticleService(db=mock_db)
        result = service.get_article(article_id=1)

        assert result.id == 1
        assert result.title == "Cached Title"
        mock_cache_instance.get.assert_called_once_with(1)
        mock_repo_instance.get.assert_not_called()

def test_get_article_cache_miss():
    """
    PRUEBA UNITARIA: Verifica que si un artículo NO está en el caché,
    se busca en la DB y luego se guarda en el caché.
    """
    mock_db = MagicMock()
    
    with patch('app.services.article_service.CacheWrapper') as MockCache, \
         patch('app.services.article_service.ArticleRepository') as MockRepo:
        
        mock_cache_instance = MockCache.return_value
        mock_repo_instance = MockRepo.return_value

        mock_cache_instance.get.return_value = None
        
        # CORRECCIÓN: Completamos el mock con todos los campos que Pydantic espera.
        mock_db_article = MagicMock()
        mock_db_article.id = 1
        mock_db_article.title = "DB Title"
        mock_db_article.body = "This body is from the database and is valid."
        mock_db_article.author = "DB Author"
        mock_db_article.tags = "tag1;tag2"
        mock_db_article.published_at = None
        mock_db_article.created_at = datetime.now()
        mock_db_article.updated_at = datetime.now()
        mock_repo_instance.get.return_value = mock_db_article
        
        service = ArticleService(db=mock_db)
        result = service.get_article(article_id=1)

        assert result.title == "DB Title"
        mock_cache_instance.get.assert_called_once_with(1)
        mock_repo_instance.get.assert_called_once_with(mock_db, 1)
        mock_cache_instance.set.assert_called_once()

def test_create_article_raises_conflict():
    """
    PRUEBA UNITARIA: Verifica que el servicio lanza una excepción HTTP 409
    si el artículo a crear ya existe.
    """
    mock_db = MagicMock()
    
    with patch('app.services.article_service.ArticleRepository') as MockRepo:
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.get_by_title_and_author.return_value = MagicMock()
        
        service = ArticleService(db=mock_db)
        # CORRECCIÓN: 'body' ahora es válido.
        payload = ArticleCreate(title="Existing", body="This body is also valid", author="Author")

        with pytest.raises(HTTPException) as exc_info:
            service.create_article(payload)
        
        assert exc_info.value.status_code == 409