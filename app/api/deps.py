from typing import Generator
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.config import settings


def get_db() -> Generator[Session, None, None]:
    """
    Provides a SQLAlchemy database session for each API request.

    This dependency is used in FastAPI routes to ensure that:
    - A new database session is created at the start of each request.
    - The session is properly closed after the request completes, even if an error occurs.

    Yields:
        Session: An active SQLAlchemy session connected to the database.
        
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_api_key(x_api_key: str | None = Header(None)):
    """
    Validates the API key provided in the request headers.

    This dependency enforces access control by requiring a valid API key 
    to be sent in the `X-API-Key` header. If the `API_KEY` setting is not 
    configured, the validation is skipped (useful for local development or testing).

    Args:
        x_api_key (str | None): The API key passed via the `X-API-Key` header.

    Raises:
        HTTPException: If the key is missing or does not match the configured API key.
        
    """
    if settings.API_KEY:  # Only enforce validation if API_KEY is set in settings
        if not x_api_key or x_api_key != settings.API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API Key",
            )
