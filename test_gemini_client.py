import pytest
from unittest.mock import patch, MagicMock
from gemini_client import extract_locations_from_text

def test_extract_locations_from_text_valid_json():
    # Mock response with valid JSON
    mock_response = MagicMock()
    mock_response.text = '["New York", "London", "Paris"]'
    
    with patch('gemini_client.genai.GenerativeModel') as mock_model:
        mock_model.return_value.generate_content.return_value = mock_response
        result = extract_locations_from_text("I visited New York, London, and Paris last year.")
        
        assert result == ["New York", "London", "Paris"]
        assert len(result) == 3

def test_extract_locations_from_text_invalid_json():
    # Mock response with invalid JSON but valid comma-separated text
    mock_response = MagicMock()
    mock_response.text = "New York, London, Paris"
    
    with patch('gemini_client.genai.GenerativeModel') as mock_model:
        mock_model.return_value.generate_content.return_value = mock_response
        result = extract_locations_from_text("I visited New York, London, and Paris last year.")
        
        assert result == ["New York", "London", "Paris"]
        assert len(result) == 3

def test_extract_locations_from_text_empty_input():
    # Test with empty input
    mock_response = MagicMock()
    mock_response.text = "[]"
    
    with patch('gemini_client.genai.GenerativeModel') as mock_model:
        mock_model.return_value.generate_content.return_value = mock_response
        result = extract_locations_from_text("")
        
        assert result == []
        assert len(result) == 0

def test_extract_locations_from_text_no_locations():
    # Test with text containing no locations
    mock_response = MagicMock()
    mock_response.text = "[]"
    
    with patch('gemini_client.genai.GenerativeModel') as mock_model:
        mock_model.return_value.generate_content.return_value = mock_response
        result = extract_locations_from_text("This is a test message with no locations.")
        
        assert result == []
        assert len(result) == 0 