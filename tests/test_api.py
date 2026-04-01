"""API tests for the capability service."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health and root endpoints."""
    
    def test_root(self, client):
        """Test root endpoint returns service info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_health(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestTextSummaryCapability:
    """Test text_summary capability."""
    
    def test_summary_success(self, client):
        """Test successful text summary."""
        long_text = "This is a long text that needs to be summarized. " * 20
        
        response = client.post("/v1/capabilities/run", json={
            "capability": "text_summary",
            "input": {
                "text": long_text,
                "max_length": 100
            },
            "request_id": "test-123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "result" in data["data"]
        assert data["meta"]["capability"] == "text_summary"
        assert data["meta"]["request_id"] == "test-123"
        assert "elapsed_ms" in data["meta"]
    
    def test_summary_short_text(self, client):
        """Test summary with short text returns original."""
        short_text = "Short text."
        
        response = client.post("/v1/capabilities/run", json={
            "capability": "text_summary",
            "input": {
                "text": short_text,
                "max_length": 100
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
    
    def test_summary_invalid_input_missing_text(self, client):
        """Test summary with missing text field."""
        response = client.post("/v1/capabilities/run", json={
            "capability": "text_summary",
            "input": {
                "max_length": 100
            }
        })
        
        assert response.status_code == 400
        data = response.json()
        assert data["ok"] is False
        assert data["error"]["code"] == "INVALID_INPUT"


class TestTextTranslateCapability:
    """Test text_translate capability."""
    
    def test_translate_success(self, client):
        """Test successful translation."""
        response = client.post("/v1/capabilities/run", json={
            "capability": "text_translate",
            "input": {
                "text": "hello",
                "target_language": "zh"
            },
            "request_id": "test-translate-1"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        result = data["data"]["result"]
        assert "translated_text" in result["result"]
        assert result["result"]["target_language"] == "zh"
    
    def test_translate_unknown_word(self, client):
        """Test translation of unknown word returns indicator."""
        response = client.post("/v1/capabilities/run", json={
            "capability": "text_translate",
            "input": {
                "text": "unknownxyz123",
                "target_language": "fr"
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True


class TestErrorHandling:
    """Test error handling."""
    
    def test_unknown_capability(self, client):
        """Test request with unknown capability."""
        response = client.post("/v1/capabilities/run", json={
            "capability": "unknown_capability",
            "input": {}
        })
        
        # Pydantic validation returns 422 for invalid Literal value
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data  # FastAPI validation error format
    
    def test_invalid_max_length(self, client):
        """Test summary with invalid max_length."""
        response = client.post("/v1/capabilities/run", json={
            "capability": "text_summary",
            "input": {
                "text": "Some text",
                "max_length": 5  # Below minimum
            }
        })
        
        assert response.status_code == 400
        data = response.json()
        assert data["ok"] is False


class TestResponseHeaders:
    """Test response headers."""
    
    def test_request_id_header(self, client):
        """Test X-Request-ID header is present."""
        response = client.post("/v1/capabilities/run", json={
            "capability": "text_summary",
            "input": {
                "text": "Test",
                "max_length": 50
            }
        })
        
        assert "X-Request-ID" in response.headers
        assert "X-Elapsed-Ms" in response.headers
