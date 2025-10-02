"""
Test the main application endpoints.
"""
import pytest


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] is True
    assert "message" in data
    assert "uptime" in data


def test_legacy_system_check(client):
    """Test legacy system check endpoint."""
    response = client.get("/system-check")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] is True
    assert data["message"] == "File Craft is up"


def test_openapi_docs(client):
    """Test that OpenAPI docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/api/openapi.json")
    assert response.status_code == 200