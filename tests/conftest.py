import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def runner():
    """Create a test CLI runner for the Flask application."""
    return app.test_cli_runner()

