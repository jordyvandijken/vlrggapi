import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app

client = TestClient(app)

@pytest.fixture
def mock_vlr():
    """Mock the VLR client responses"""
    with patch("main.vlr") as mock:
        yield mock

class TestHealthEndpoint:
    """Tests for the health check endpoint"""
    
    def test_health_endpoint(self):
        """Test that the health endpoint returns a 200 status"""
        response = client.get("/health")
        assert response.status_code == 200
        assert "status" in response.json()
        assert response.json()["status"] == "healthy"

class TestNewsEndpoint:
    """Tests for the news endpoint"""
    
    def test_news_endpoint(self, mock_vlr):
        """Test that the news endpoint returns data properly"""
        # Mock the return value
        mock_data = {
            "data": {
                "status": 200,
                "segments": [
                    {
                        "title": "Test Article",
                        "description": "This is a test article",
                        "date": "May 5, 2025",
                        "author": "Test Author",
                        "url_path": "/123/test-article"
                    }
                ]
            }
        }
        mock_vlr.vlr_recent.return_value = mock_data
        
        # Make the request
        response = client.get("/news")
        
        # Check the response
        assert response.status_code == 200
        assert response.json() == mock_data
        mock_vlr.vlr_recent.assert_called_once()

# Add more test classes for other endpoints as needed