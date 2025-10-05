import json
from redis import Redis
from typing import Optional, Dict, Any
from app.core.config import settings

# Cliente de Redis inicializado desde la URL de configuración.
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

class CacheWrapper:
    """
    Redis cache client and wrapper for the Article service.

    This module provides a lightweight abstraction layer over Redis,
    offering helper methods to cache, retrieve, and invalidate article data.
    It ensures consistent key naming, JSON serialization, and time-to-live (TTL)
    management based on the application settings.

    Attributes:
        redis_client (Redis):
            A global Redis client instance initialized using the configured URL.

    Classes:
        CacheWrapper:
            Provides simple methods for interacting with Redis, including:
                - get(article_id): Retrieve a cached article by ID.
                - set(article_id, data): Store an article with a defined TTL.
                - invalidate(article_id): Remove a cached article by ID.

    """
    @staticmethod
    def _get_article_key(article_id: int) -> str:
        return f"article:{article_id}"

    def get(self, article_id: int) -> Optional[Dict[str, Any]]:
        key = self._get_article_key(article_id)
        cached_data = redis_client.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None

    def set(self, article_id: int, data: Dict[str, Any]) -> None:
        key = self._get_article_key(article_id)
        redis_client.set(key, json.dumps(data, default=str), ex=settings.CACHE_TTL_SECONDS)

    def invalidate(self, article_id: int) -> None:
        key = self._get_article_key(article_id)
        redis_client.delete(key)