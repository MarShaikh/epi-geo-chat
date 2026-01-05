import pytest
from unittest.mock import patch, MagicMock
from src.stac.geocoding import GeoCodingService


class TestGeoCodingServiceUnit:
    """Unit tests with mocked dependencies"""

    @pytest.mark.asyncio
    async def test_geocode_local_lookup_lagos(self):
        """Test geocoding Lagos hits local lookup"""
        geocoder = GeoCodingService()

        result = await geocoder.geocode("Lagos")

        assert result is not None
        assert result["name"] == "Lagos"
        assert result["source"] == "local"
        assert "bbox" in result
        assert len(result["bbox"]) == 4
        # Verify Lagos coordinates
        assert result["bbox"][0] == pytest.approx(2.70, rel=0.01)

    @pytest.mark.asyncio
    @patch("src.stac.geocoding.MapsSearchClient")
    async def test_geocode_azure_maps_success(self, mock_maps_client):
        """Test geocoding with Azure Maps for unknown location"""
        # Setup mock
        mock_client_instance = MagicMock()
        mock_maps_client.return_value = mock_client_instance

        mock_response = {
            "features": [
                {
                    "bbox": [3.3, 6.4, 3.5, 6.6],
                    "properties": {
                        "address": {
                            "formattedAddress": "Ijoma Place, Nigeria",
                            "countryRegion": {"name": "Nigeria"},
                        }
                    },
                }
            ]
        }
        mock_client_instance.get_geocoding.return_value = mock_response

        geocoder = GeoCodingService()
        result = await geocoder.geocode("Ijoma Place, Nigeria")

        assert result is not None
        assert "Ijoma Place" in result["name"]
        assert result["source"] == "azure_maps"
        assert result["bbox"] == [3.3, 6.4, 3.5, 6.6]
        mock_client_instance.get_geocoding.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.stac.geocoding.MapsSearchClient")
    async def test_geocode_no_results(self, mock_maps_client):
        """Test geocoding returns None for invalid location"""
        mock_client_instance = MagicMock()
        mock_maps_client.return_value = mock_client_instance
        mock_response = {"features": []}
        mock_client_instance.get_geocoding.return_value = mock_response

        geocoder = GeoCodingService()
        result = await geocoder.geocode("Woolpack Lane")

        assert result is None

    @pytest.mark.asyncio
    @patch("src.stac.geocoding.MapsSearchClient")
    async def test_geocode_filters_nigeria_only(self, mock_maps_client):
        """Test that geocoding filters results to Nigeria only"""
        mock_client_instance = MagicMock()
        mock_maps_client.return_value = mock_client_instance

        # Mock response with Portugal Lagos and Nigeria Lagos
        mock_response = {
            "features": [
                {
                    "bbox": [0.0, 51.0, 0.1, 51.1],
                    "properties": {
                        "address": {
                            "formattedAddress": "Lagos, Portugal",
                            "countryRegion": {"name": "Portugal"},
                        }
                    },
                },
                {
                    "bbox": [3.3, 6.4, 3.5, 6.6],
                    "properties": {
                        "address": {
                            "formattedAddress": "Lagos, Nigeria",
                            "countryRegion": {"name": "Nigeria"},
                        }
                    },
                },
            ]
        }
        mock_client_instance.get_geocoding.return_value = mock_response

        geocoder = GeoCodingService()
        result = await geocoder.geocode("Lagos city")

        assert result is not None
        assert "Nigeria" in result["name"]
        assert result["bbox"][0] >= 2.31  # Within Nigeria bbox

    @pytest.mark.asyncio
    async def test_geocode_result_format(self):
        """Test that geocode result has correct format"""
        geocoder = GeoCodingService()
        result = await geocoder.geocode("Lagos")

        assert isinstance(result, dict)
        assert "name" in result
        assert "bbox" in result
        assert "source" in result
        assert isinstance(result["bbox"], list)
        assert len(result["bbox"]) == 4
        # Verify bbox format: [min_lon, min_lat, max_lon, max_lat]
        assert result["bbox"][0] < result["bbox"][2]  # min_lon < max_lon
        assert result["bbox"][1] < result["bbox"][3]  # min_lat < max_lat
