from unittest.mock import patch, MagicMock
import pytest
from src.stac.catalog_client import GeoCatalogClient


@patch('src.stac.catalog_client.DefaultAzureCredential')
@patch('src.stac.catalog_client.requests.get')
@patch('src.stac.catalog_client.pystac.Item.from_dict')
def test_get_item_success(mock_from_dict, mock_get, mock_credential):
    """Test successful retrieval of a specific item"""
    # Setup mocks
    mock_token = MagicMock()
    mock_token.token = "test-token"
    mock_credential_instance = MagicMock()
    mock_credential_instance.get_token.return_value = mock_token
    mock_credential.return_value = mock_credential_instance
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "item-123", "type": "Feature"}
    mock_get.return_value = mock_response
    
    mock_item = MagicMock()
    mock_from_dict.return_value = mock_item
    
    # Setup environment
    with patch.dict('os.environ', {
        'GEOCATALOG_URL': 'https://test-catalog.com',
        'GEOCATALOG_SCOPE': 'https://test.scope/.default'
    }, clear=True):
        client = GeoCatalogClient()
        result = client.get_item("collection-1", "item-123")
        
        # Verify request was made correctly
        mock_get.assert_called_once_with(
            'https://test-catalog.com/stac/collections/collection-1/items/item-123',
            headers={"Authorization": "Bearer test-token"},
            params={"api-version": "2025-04-03-preview"}
        )
        
        # Verify response handling
        mock_response.raise_for_status.assert_called_once()
        mock_from_dict.assert_called_once_with(
            {"id": "item-123", "type": "Feature"},
            migrate=True
        )
        
        assert result == mock_item


@patch('src.stac.catalog_client.DefaultAzureCredential')
@patch('src.stac.catalog_client.requests.get')
def test_get_item_http_error(mock_get, mock_credential):
    """Test get_item raises exception on HTTP error"""
    # Setup mocks
    mock_token = MagicMock()
    mock_token.token = "test-token"
    mock_credential_instance = MagicMock()
    mock_credential_instance.get_token.return_value = mock_token
    mock_credential.return_value = mock_credential_instance
    
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("404 Not Found")
    mock_get.return_value = mock_response
    
    # Setup environment
    with patch.dict('os.environ', {
        'GEOCATALOG_URL': 'https://test-catalog.com',
        'GEOCATALOG_SCOPE': 'https://test.scope/.default'
    }, clear=True):
        client = GeoCatalogClient()
        
        with pytest.raises(Exception, match="404 Not Found"):
            client.get_item("collection-1", "nonexistent-item")


@patch('src.stac.catalog_client.DefaultAzureCredential')
@patch('src.stac.catalog_client.requests.get')
@patch('src.stac.catalog_client.pystac.Item.from_dict')
def test_get_item_uses_auth_headers(mock_from_dict, mock_get, mock_credential):
    """Test that get_item uses authentication headers from _get_headers"""
    # Setup mocks
    mock_token = MagicMock()
    mock_token.token = "secure-token-456"
    mock_credential_instance = MagicMock()
    mock_credential_instance.get_token.return_value = mock_token
    mock_credential.return_value = mock_credential_instance
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "item-456"}
    mock_get.return_value = mock_response
    
    mock_from_dict.return_value = MagicMock()
    
    # Setup environment
    with patch.dict('os.environ', {
        'GEOCATALOG_URL': 'https://test-catalog.com',
        'GEOCATALOG_SCOPE': 'https://test.scope/.default'
    }, clear=True):
        client = GeoCatalogClient()
        client.get_item("collection-2", "item-456")
        
        # Verify the correct auth header was used
        call_args = mock_get.call_args
        assert call_args.kwargs['headers'] == {"Authorization": "Bearer secure-token-456"}