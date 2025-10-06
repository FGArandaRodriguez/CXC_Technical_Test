from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from redis import RedisError
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import SessionLocal
from app.core.config import settings
from app.api.v1 import articles
from app.api.deps import require_api_key, rate_limiter
from app.cache.redis_wrapper import get_redis_client
from app.cache.redis_wrapper import redis_client
from sqlalchemy import text


app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.middleware("http")(rate_limiter)
#app.include_router(articles.router, prefix=settings.API_V1_STR)

# CORS configuration to allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the Articles router with a prefix and global API Key protection
app.include_router(
    articles.router,
    prefix=settings.API_V1_STR,
    tags=["Articles"],
    dependencies=[Depends(require_api_key)]
)

router = APIRouter()

@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint.

    Returns a simple status message confirming that the API service is running
    and reachable. Useful for uptime monitoring or container orchestration
    probes (e.g., Kubernetes liveness/readiness checks).

    Returns:
        dict: A JSON response containing the status message.
    """
    status = {"status": "ok", "database": "ok", "redis": "ok"}

    # Chequeo DB
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception:
        status["status"] = "degraded"
        status["database"] = "error"

    # Chequeo Redis
    try:
        if redis_client is None or not redis_client.ping():
            raise Exception("Redis no disponible")
    except Exception:
        status["status"] = "degraded"
        status["redis"] = "error"

    return status
