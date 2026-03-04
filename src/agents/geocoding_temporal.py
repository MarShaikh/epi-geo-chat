from typing import Optional, List, Annotated, Dict
from pydantic import BaseModel, Field
from src.agents.agent_config import create_agent_client
from src.stac.geocoding import GeoCodingService
from src.utils.datetime_parser import format_datetime
from datetime import datetime


class GeocodingResult(BaseModel):
    """Structured output for geocoding and temporal resolution."""

    bbox: Annotated[
        Optional[List[float]],
        Field(
            default=None,
            description="Bounding box [min_lon, min_lat, max_lon, max_lat]",
        ),
    ]
    datetime: Annotated[
        Optional[str],
        Field(
            default=None,
            description="ISO 8601 datetime or range (YYYY-MM-DD or YYYY-MM-DD/YYYY-MM-DD)",
        ),
    ]
    location_source: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Source of geocoding result: local, azure_maps, or llm",
        ),
    ]


async def geocode(
    location: Annotated[str, Field(description="Location name to geocode")],
) -> Optional[Dict]:
    """
    Geocode a location name to a bounding box.

    Returns:
        Dict with name, bbox, and source fields, or None if geocoding fails.
    """
    geocoder = GeoCodingService()
    return await geocoder.geocode(location)


def create_geocoding_agent():
    """
    Agent 2: Resolve location and temporal references.

    Uses geocoder.geocode() as a function tool for location resolution.
    The LLM handles temporal resolution.
    Returns structured output using GeocodingResult Pydantic model.
    """

    # Get the current date for relative time calculations
    current_date = datetime.today().strftime("%Y-%m-%d")

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

    For temporal references:
    - First resolve the meaning to a date range (e.g. "last month" → "2026-01-01/2026-01-31", relative to {current_date})
    - Then ALWAYS call format_datetime() with the resolved date string to ensure proper ISO 8601 formatting with T separators
    - Examples of what to pass to format_datetime():
      - "2024-01-01/2024-12-31" (for "2024")
      - "2023-03-01/2023-03-31" (for "March 2023")
      - "2026-01-01/2026-01-31" (for "last month")
    - If datetime is None or not provided, set datetime to None

    IMPORTANT: You MUST call format_datetime() for every non-null datetime before returning.

    Return the bbox, datetime, and location_source in the structured format.
    """
    agent_client = create_agent_client()
    geocoding_agent = agent_client.as_agent(
        name="GeocodingTemporalAgent", instructions=instructions, tools=[geocode, format_datetime]
    )
    return geocoding_agent
