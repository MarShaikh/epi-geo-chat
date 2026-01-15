from typing import Dict, List, Optional, Annotated
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


def search_and_summarize(
    collections: Annotated[
        List[str], Field(description="List of STAC collection IDs to search")
    ],
    bbox: Annotated[
        Optional[List[float]],
        Field(description="Bounding box [min_lon, min_lat, max_lon, max_lat]"),
    ] = None,
    datetime: Annotated[
        Optional[str],
        Field(
            description="ISO 8601 datetime or range (YYYY-MM-DD or YYYY-MM-DD/YYYY-MM-DD)"
        ),
    ] = None,
    limit: Annotated[
        Optional[int],
        Field(description="Maximum number of items to retrieve (default 100)"),
    ] = 10,
) -> Dict:
    """
    Perform STAC seach and return structured summary of results for the agent.

    This function processes STAC results deterministically in Python,
    avoiding the need to send 61K tokens of raw JSON to the LLM.

    The agent receives only a concise summary (~1K tokens).
    Args:
        collections: List of STAC collection IDs to search
        bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
        datetime: ISO 8601 datetime or range (YYYY-MM-DD or YYYY-MM-DD/YYYY-MM-DD)
        limit: Maximum number of items to retrieve (default 100)
    Returns:
        dict: Summarized results with count, date range, and sample item IDs
    """

    catalog_client = GeoCatalogClient()

    # perform the search
    search_results = catalog_client.search(
        bbox=bbox,
        datetime=datetime,
        collections=collections,
        limit=limit,
    )

    items = search_results.get("features", [])

    if not items:
        return {
            "count": 0,
            "collections": collections,
            "date_range": datetime if datetime else "Unspecified",
            "items": [],
            "bbox_searched": bbox if bbox else "Unspecified",
        }

    # extract datetimes from items
    dates = []
    for item in items:
        if "properties" in item and "datetime" in item["properties"]:
            dt = item["properties"]["datetime"]
            if dt:
                dates.append(dt)

    # determine date range
    if dates:
        dates_sorted = sorted(dates)
        date_range = f"{dates_sorted[0]} to {dates_sorted[-1]}"

    else:
        date_range = "Unspecified"

    # get sample item IDs (limit to first 10)
    sample_items = [item["id"] for item in items[:10]]

    return {
        "count": len(items),
        "collections": collections,
        "date_range": date_range,
        "items": sample_items,
        "bbox_searched": bbox if bbox else "Unspecified",
    }


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

    agent_client = create_agent_client()
    catalog_agent = agent_client.create_agent(
        name="STACCoordinatorAgent",
        instructions=instructions,
        tools=search_and_summarize,
    )
    return catalog_agent
