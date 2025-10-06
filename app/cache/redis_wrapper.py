import json
from redis import Redis, RedisError
from typing import Optional, Dict, Any
from app.core.config import settings

# Cliente de Redis inicializado desde la URL de configuración.
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_redis_client() -> Optional[Redis]:
    """
    Devuelve el cliente Redis si está disponible, de lo contrario None.
    """
    try:
        redis_client.ping()
        return redis_client
    except RedisError:
        # Redis no disponible
        return None

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
        client = get_redis_client()
        if not client:
            return None
        try:
            cached_data = client.get(self._get_article_key(article_id))
            if cached_data:
                return json.loads(cached_data)
        except RedisError:
            return None
        return None

    def set(self, article_id: int, data: Dict[str, Any]) -> None:
        client = get_redis_client()
        if not client:
            return
        try:
            client.set(
                self._get_article_key(article_id),
                json.dumps(data, default=str),
                ex=settings.CACHE_TTL_SECONDS
            )
        except RedisError:
            pass

    def invalidate(self, article_id: int) -> None:
        client = get_redis_client()
        if not client:
            return
        try:
            client.delete(self._get_article_key(article_id))
        except RedisError:
            pass