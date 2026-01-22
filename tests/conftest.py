import os
import pytest
from fastapi.testclient import TestClient

# Set database URL before importing app
os.environ["POSTGRES_URL"] = "postgresql://testuser:testpass@localhost:5432/testdb"

from app import app, get_db_engine


@pytest.fixture(scope="session")
def db_engine():
    """Create a database engine for the test session."""
    engine = get_db_engine()
    yield engine
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def verify_db_connection(db_engine):
    """Verify database connection is available before running tests."""
    from sqlalchemy import text
    
    try:
        with db_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        pytest.exit(f"Cannot connect to test database: {e}")


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)
