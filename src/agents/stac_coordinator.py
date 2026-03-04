from datetime import datetime
from typing import Dict, List, Optional, Annotated, Any
from pydantic import BaseModel, Field
from src.agents.agent_config import create_agent_client
from src.stac.catalog_client import GeoCatalogClient
from src.utils.datetime_parser import format_datetime as _format_datetime


class STACItem(BaseModel):
    """Individual STAC item summary."""

    id: Annotated[str, Field(description="Unique identifier for the STAC item")]
    datetime: Annotated[str, Field(description="Datetime of the observation")]
    assets: Annotated[
        List[str],
        Field(description="List of available asset keys (e.g., 'COG', 'metadata')"),
    ]


class STACSearchResult(BaseModel):
    """Structured output for STAC search results."""

    count: Annotated[Optional[int], Field(description="Total number of items found")]
    description: Annotated[
        Optional[str],
        Field(default=None, description="Description of the search results"),
    ]
    keywords: Annotated[
        Optional[List[str]],
        Field(default=None, description="Keywords associated with the results"),
    ]
    license: Annotated[
        Optional[str],
        Field(default=None, description="License information for the data"),
    ]
    collections: Annotated[
        List[str], Field(description="Collections that were searched")
    ]
    date_range: Annotated[str, Field(description="Date range covered by the results")]
    items: Annotated[
        Optional[List[STACItem]],
        Field(
            default=None,
            description="Summary of found items (limited to first 10 for brevity)",
        ),
    ]
    bbox_searched: Annotated[
        Optional[List[float]],
        Field(
            default=None,
            description="Bounding box that was searched [min_lon, min_lat, max_lon, max_lat]",
        ),
    ]


def list_collections() -> Dict:
    """
    List all available STAC collections from the catalog.

    Use this when the user asks:
    - "What collections are available?"
    - "List all the available datasets."
    - "Show me all the data sources."

    Returns:
        Dict: Collection count a list of collection IDs with titles and descriptions.
    """
    print("Listing all STAC collections...")
    catalog_client = GeoCatalogClient()
    response = catalog_client.list_collections()

    collections = []
    for coll in response.get("collections", []):
        collections.append(
            {
                "id": coll["id"],
                "title": coll.get("title", ""),
                "description": coll.get("description", ""),
            }
        )

    return {"count": len(collections), "collections": collections}


def get_collection_details(
    collection_id: Annotated[str, Field(description="STAC collection ID")],
) -> Dict[str, Any]:
    """
    Get detailed information about a specific STAC collection.

    Use this when the user asks about a specific data type:
    - "What do you know about vegetation data?"
    - "Tell me about the temperature collections"
    - "Give me details on modis-11A1-061-nigeria-557"

    Args:
        collection_id: The STAC collection ID to get details for

    Returns:
        Detailed collection metadata including description, extent, keywords, license.
    """
    print(f"Fetching details for collection ID: {collection_id}")
    catalog_client = GeoCatalogClient()

    try:
        coll_info = catalog_client.get_collection(collection_id)

        bounding_box = coll_info.get("extent", "").get("spatial", {}).get("bbox", [])[0]

        datetime_0 = (
            coll_info.get("extent", "").get("temporal", {}).get("interval", [])[0][0]
        )
        datetime_1 = (
            coll_info.get("extent", "").get("temporal", {}).get("interval", [])[0][1]
        )

        # if datetime_1 is None, set it to current datetime in ISO format since
        # ongoing collections may have open-ended temporal extent
        if datetime_1 is None:
            datetime_1 = datetime.now().isoformat()

        datetime_range = (datetime_0, datetime_1)
        return {
            "id": collection_id,
            "description": coll_info.get("description", ""),
            "keywords": coll_info.get("keywords", []),
            "bounding_box": bounding_box,
            "date_extent": datetime_range,
            "license": coll_info.get("license", ""),
            "providers": coll_info.get("providers", []),
        }
    except Exception as e:
        return {"id": collection_id, "error": str(e)}


def search_and_summarize(
    collections: Annotated[
        Optional[List[str]], Field(description="List of STAC collection IDs to search")
    ] = None,
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

    # Ensure datetime has T separators required by GeoCatalog API
    if datetime:
        datetime = _format_datetime(datetime)

    # if no collections specified, search all
    if not collections:
        all_collections_resp = catalog_client.list_collections()
        collections = [
            coll["id"] for coll in all_collections_resp.get("collections", [])
        ]

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

    Handles both data search AND metadata queries using the appropriate function tool.

    Tools available:
    - list_collection_names(): To list all available STAC collections
    - get_collection_details(collection_id): To get details about a specific collection
    - search_and_summarize():  To perform STAC searches and summarize results

    Returns:
        Structured output using STACSearchResult Pydantic model with nested STACItem objects.
    """

    instructions = """
    You are a STAC (SpatioTemporal Asset Catalog) coordinator agent.

    CRITICAL RULES:
    - Make EXACTLY ONE tool call per request, then return your structured response immediately.
    - NEVER call the same tool twice. NEVER call multiple tools.
    - After receiving a tool result, format it into the response schema and STOP.

    TOOL SELECTION (pick ONE based on intent):

    Intent: "data_search" or "analysis"
      → Call search_and_summarize(collections, bbox, datetime) ONCE
      → Return the result as structured output

    Intent: "metadata_query"
      Sub-intent "list_collections":
        → Call list_collections() ONCE
      Sub-intent "collection_details":
        → Call get_collection_details(collection_id) ONCE
      Sub-intent "count_items":
        → Call search_and_summarize() with limit=1000 ONCE

    FAILURE CONDITIONS (stop and return immediately):
    - Tool returns 0 items → set count=0, return the result
    - Tool returns an error → set count=0, include error in description, return
    - No collections provided → set count=0, return

    After your single tool call completes, return your structured response. Do NOT retry, do NOT call another tool.
    """

    agent_client = create_agent_client()
    catalog_agent = agent_client.as_agent(
        name="STACCoordinatorAgent",
        instructions=instructions,
        tools=[search_and_summarize, list_collections, get_collection_details],
    )
    return catalog_agent
