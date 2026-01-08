from typing import List, Optional
from pydantic import BaseModel, Field
from src.agents.agent_config import create_agent_client
from src.stac.catalog_client import GeoCatalogClient


class STACItem(BaseModel):
    """Individual STAC item summary."""

    id: str = Field(description="Unique identifier for the STAC item")
    datetime: str = Field(description="Datetime of the observation")
    assets: List[str] = Field(
        description="List of available asset keys (e.g., 'COG', 'metadata')"
    )


class STACSearchResult(BaseModel):
    """Structured output for STAC search results."""

    count: int = Field(description="Total number of items found")
    collections: List[str] = Field(description="Collections that were searched")
    date_range: str = Field(description="Date range covered by the results")
    items: List[STACItem] = Field(
        description="Summary of found items (limited to first 10 for brevity)"
    )
    bbox_searched: Optional[List[float]] = Field(
        default=None,
        description="Bounding box that was searched [min_lon, min_lat, max_lon, max_lat]",
    )


def create_stac_coordinator_agent():
    """
    Agent 3: Execute STAC catalog searches and optimize results.

    Uses catalog_client.search() as a function tool.
    Returns structured output using STACSearchResult Pydantic model with nested STACItem objects.
    """

    instructions = """
    You are a STAC (SpatioTemporal Asset Catalog) coordinator agent for geospatial data queries.

    Your responsibilities include:
    1. Take parsed query parameters (collections, bbox, datetime)
    2. Execute STAC API searches using the search() function tool
    3. Optimize and filter results
    4. Return a structured summary of findings

    When you receive search parameters:
    - Call the search() function tool with the appropriate parameters
    - Analyze the returned results
    - Extract key information from each item:
      - Item ID
      - Datetime of observation
      - Available assets (COG, metadata, etc.)
    - Summarize the overall search results

    Return a structured response with:
    - Total count of items found
    - Collections searched
    - Date range covered
    - Detailed list of items (limit to first 10 items for efficiency)
    - Bounding box that was searched
    """

    catalog_client = GeoCatalogClient()
    agent_client = create_agent_client()
    catalog_agent = agent_client.create_agent(
        name="STACCoordinatorAgent",
        instructions=instructions,
        tools=catalog_client.search,
    )
    return catalog_agent
