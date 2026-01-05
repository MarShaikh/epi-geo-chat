from src.agents.agent_config import create_agent_client
from src.stac.geocoding import GeoCodingService


def create_geocoding_agent():
    """
    Agent 2: Resolve location and temporal references

    This agent uses a helper function for actual geocoding, but the temporal resolution is handled by the LLM.
    """

    instructions = """
    You are a geocoding and temporal resolution agent for geospatial data queries.

    Your tasks are:
    1. Take location names and convert them into bounding boxes.
    2. Convert relative time references to ISO 8601 format.

    For location, you will be provided with geocoding results.
    For temporal references, convert:
    - "last month" -> calculate last month's date range (YYYY-MM-DD/YYYY-MM-DD)
    - "yesterday" -> calculate yesterday's date (YYYY-MM-DD)
    - "last week" or "last 7 days" -> calculate last 7 days date range (YYYY-MM-DD/YYYY-MM-DD)
    - "2024" -> "2024-01-01/2024-12-31"
    - If already in ISO format, return as is. 

    Return in JSON format: 
    {
        "bbox": [min_lon, min_lat, max_lon, max_lat] or null,
        "datetime": "YYYY-MM-DD/YYYY-MM-DD" or "YYYY-MM-DD"
    }
    """
    geocoder = GeoCodingService()
    agent_client = create_agent_client()
    geocoding_agent = agent_client.create_agent(
        name="GeocodingTemporalAgent", instructions=instructions, tools=geocoder.geocode
    )
    return geocoding_agent
