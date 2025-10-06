import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.core.config import settings
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Crea todas las tablas necesarias antes de ejecutar los tests."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Crea una sesión nueva por test para aislar los cambios.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client():
    """Proporciona un cliente de prueba con API Key configurada."""
    with TestClient(app) as c:
        c.headers.update({"x-api-key": settings.API_KEY})
        yield c
