from typing import Generator
from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from redis.exceptions import RedisError

from app.db.session import SessionLocal
from app.core.config import settings
from app.cache.redis_wrapper import redis_client # Usamos el cliente ya configurado

def get_db() -> Generator[Session, None, None]:
    """
    Proporciona una sesión de base de datos de SQLAlchemy para cada petición de la API.

    Esta dependencia asegura que se cree una nueva sesión al inicio de cada
    petición y que se cierre correctamente al finalizar, incluso si ocurre un error.

    Yields:
        Session: Una sesión activa de SQLAlchemy conectada a la base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_api_key(x_api_key: str | None = Header(None, alias="X-API-Key")):
    """
    Valida la API key proporcionada en la cabecera de la petición.

    Esta dependencia impone control de acceso requiriendo una API key válida
    en la cabecera `X-API-Key`. Si la variable `API_KEY` no está configurada,
    la validación se omite (útil para desarrollo local).

    Args:
        x_api_key (str | None): La API key pasada a través de la cabecera `X-API-Key`.

    Raises:
        HTTPException: Si la clave falta o no coincide con la configurada.
    """
    if settings.API_KEY:
        if not x_api_key or x_api_key != settings.API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API Key",
            )


async def rate_limiter(request: Request, call_next):
    """
    Middleware de Rate Limiting simple basado en Redis.

    - Identifica a los clientes por su dirección IP.
    - Permite un máximo de `RATE_LIMIT_MAX_REQUESTS` peticiones por
      ventana de `RATE_LIMIT_WINDOW` segundos.
    - Devuelve una respuesta HTTP 429 si se excede el límite.
    - Maneja fallos de Redis de forma segura, permitiendo que la API continúe
      funcionando si el servicio de Redis no está disponible.
    """
    client_ip = request.client.host if request.client else "unknown"
    key = f"ratelimit:{client_ip}"

    try:
        # Usamos una pipeline para asegurar que INCR y EXPIRE sean atómicos
        p = redis_client.pipeline()
        p.incr(key)
        p.expire(key, settings.RATE_LIMIT_WINDOW)
        request_count = p.execute()[0]

        if request_count > settings.RATE_LIMIT_MAX_REQUESTS:
            # SOLUCIÓN: Devolver una JSONResponse en lugar de lanzar una excepción
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": f"Rate limit exceeded. Try again in {settings.RATE_LIMIT_WINDOW} seconds."}
            )

    except RedisError:
        # Si Redis falla, simplemente registramos el error y continuamos
        # sin aplicar el rate limiting.
        print("RedisError: Skipping rate limiting.")

    # Si todo está bien, pasamos la petición al siguiente manejador
    response = await call_next(request)
    return response