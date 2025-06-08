import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
import os

client = TestClient(app)

# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        "API_KEY": "test_api_key",
        "GOOGLE_API_KEY": "test_google_api_key"
    }):
        yield

def test_get_coordinates_success():
    # Mock the dependencies
    with patch('main.extract_locations_from_text') as mock_extract, \
         patch('main.get_coordinates') as mock_coords:
        
        # Setup mocks
        mock_extract.return_value = ["New York", "London"]
        mock_coords.return_value = (40.7128, -74.0060)  # New York coordinates
        
        # Make request
        response = client.post(
            "/get-coordinates",
            json={"text": "I visited New York and London"},
            headers={"X-API-Key": "test_api_key"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["coordinates"]) == 2
        assert data["coordinates"][0]["location_name"] == "New York"
        assert data["coordinates"][0]["latitude"] == 40.7128
        assert data["coordinates"][0]["longitude"] == -74.0060

def test_get_coordinates_invalid_api_key():
    response = client.post(
        "/get-coordinates",
        json={"text": "I visited New York"},
        headers={"X-API-Key": "invalid_key"}
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Could not validate API key"

def test_get_coordinates_missing_api_key():
    response = client.post(
        "/get-coordinates",
        json={"text": "I visited New York"}
    )
    
    assert response.status_code == 403

def test_get_coordinates_no_locations():
    with patch('main.extract_locations_from_text') as mock_extract:
        mock_extract.return_value = []
        
        response = client.post(
            "/get-coordinates",
            json={"text": "This is a test message with no locations"},
            headers={"X-API-Key": "test_api_key"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["coordinates"]) == 0

def test_get_coordinates_invalid_request():
    response = client.post(
        "/get-coordinates",
        json={},  # Missing required 'text' field
        headers={"X-API-Key": "test_api_key"}
    )
    
    assert response.status_code == 422  # Validation error 