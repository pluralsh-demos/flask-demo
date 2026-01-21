import json
import os
from unittest.mock import patch, MagicMock

import pytest


class TestIndexEndpoint:
    """Tests for the hello world endpoint."""

    def test_index_returns_200(self, client):
        """Test that the index endpoint returns a 200 status code."""
        response = client.get('/')
        assert response.status_code == 200

    def test_index_returns_json(self, client):
        """Test that the index endpoint returns JSON content."""
        response = client.get('/')
        assert response.content_type == 'application/json'

    def test_index_message_content(self, client):
        """Test that the index endpoint returns the expected message."""
        response = client.get('/')
        data = json.loads(response.data)
        assert data['message'] == 'Hello from Flask!'
        assert data['status'] == 'running'


class TestReadyEndpoint:
    """Tests for the readiness probe endpoint."""

    def test_ready_returns_200(self, client):
        """Test that the ready endpoint returns a 200 status code."""
        response = client.get('/ready')
        assert response.status_code == 200

    def test_ready_returns_true(self, client):
        """Test that the ready endpoint indicates readiness."""
        response = client.get('/ready')
        data = json.loads(response.data)
        assert data['ready'] is True


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_without_db_url_returns_503(self, client):
        """Test that health check returns 503 when POSTGRES_URL is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Reload app module to pick up the missing env var
            import app as app_module
            original_url = app_module.DATABASE_URL
            app_module.DATABASE_URL = None
            
            response = client.get('/health')
            assert response.status_code == 503
            data = json.loads(response.data)
            assert data['status'] == 'unhealthy'
            assert data['database'] == 'not_configured'
            
            # Restore
            app_module.DATABASE_URL = original_url

    def test_health_with_db_connection_success(self, client):
        """Test health check returns 200 when database connection succeeds."""
        import app as app_module
        
        # Mock the database engine and connection
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (1,)
        mock_connection.execute.return_value = mock_result
        mock_connection.__enter__ = MagicMock(return_value=mock_connection)
        mock_connection.__exit__ = MagicMock(return_value=False)
        mock_engine.connect.return_value = mock_connection
        
        original_url = app_module.DATABASE_URL
        app_module.DATABASE_URL = "postgresql://test:test@localhost/test"
        
        with patch.object(app_module, 'get_db_engine', return_value=mock_engine):
            response = client.get('/health')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'healthy'
            assert data['database'] == 'connected'
        
        # Restore
        app_module.DATABASE_URL = original_url

    def test_health_with_db_connection_failure(self, client):
        """Test health check returns 503 when database connection fails."""
        import app as app_module
        from sqlalchemy.exc import SQLAlchemyError
        
        mock_engine = MagicMock()
        mock_engine.connect.side_effect = SQLAlchemyError("Connection refused")
        
        original_url = app_module.DATABASE_URL
        app_module.DATABASE_URL = "postgresql://test:test@localhost/test"
        
        with patch.object(app_module, 'get_db_engine', return_value=mock_engine):
            response = client.get('/health')
            assert response.status_code == 503
            data = json.loads(response.data)
            assert data['status'] == 'unhealthy'
            assert data['database'] == 'error'
        
        # Restore
        app_module.DATABASE_URL = original_url

