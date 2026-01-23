from typing import Optional, List
from pydantic import BaseModel, Field
from src.agents.agent_config import create_agent_client
from src.stac.geocoding import GeoCodingService
from datetime import datetime


class GeocodingResult(BaseModel):
    """Structured output for geocoding and temporal resolution."""

    bbox: Optional[List[float]] = Field(
        default=None, description="Bounding box [min_lon, min_lat, max_lon, max_lat]"
    )
    datetime: Optional[str] = Field(
        default=None,
        description="ISO 8601 datetime or range (YYYY-MM-DD or YYYY-MM-DD/YYYY-MM-DD)",
    )
    location_source: Optional[str] = Field(
        default=None,
        description="Source of geocoding result: local, azure_maps, or llm",
    )


def create_geocoding_agent():
    """
    Agent 2: Resolve location and temporal references.

    Uses geocoder.geocode() as a function tool for location resolution.
    The LLM handles temporal resolution.
    Returns structured output using GeocodingResult Pydantic model.
    """
    
    # Get the current date for relative time calculations
    current_date = datetime.today().strftime('%Y-%m-%d')

    instructions = f"""
    You are a geocoding and temporal resolution agent for geospatial data queries.

    Your tasks are:
    1. Take location names and convert them into bounding boxes using the geocode() function tool
    2. Convert relative time references to ISO 8601 format

    If location is provided:
    - Call the geocode() function tool with the location name
    - The tool will return bbox and source information
    - Use the returned bbox in your response

    Otherwise, if location is None:
    - Set bbox to None
    - Set location_source to None

    For temporal references, convert:
    - "last month" -> calculate last month's date range (YYYY-MM-DD/YYYY-MM-DD) relative to {current_date}
    - "yesterday" -> calculate yesterday's date (YYYY-MM-DD) relative to {current_date}
    - "last week" or "last 7 days" -> calculate last 7 days date range (YYYY-MM-DD/YYYY-MM-DD) relative to {current_date}
    - "2024" -> "2024-01-01/2024-12-31"
    - "March 2023" -> "2023-03-01/2023-03-31"
    - If already in ISO format, return as is

    Return the bbox, datetime, and location_source in the structured format.
    """
    geocoder = GeoCodingService()
    agent_client = create_agent_client()
    geocoding_agent = agent_client.as_agent(
        name="GeocodingTemporalAgent", instructions=instructions, tools=geocoder.geocode
    )
    return geocoding_agent
