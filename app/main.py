from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import articles
from app.api.deps import require_api_key

# FastAPI application initialization
app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

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
    prefix=f"{settings.API_V1_STR}/articles",
    tags=["Articles"],
    dependencies=[Depends(require_api_key)]
)

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
    return {"status": "ok"}
