"""
Agent runner functions for the multi-agent workflow.

Each function wraps an agent with observability tracing and handles
the execution logic for a specific step in the workflow pipeline.
"""

from typing import Any, List, Optional

from src.agents.query_parser import create_query_parser_agent, ParsedQuery
from src.agents.geocoding_temporal import create_geocoding_agent, GeocodingResult
from src.agents.stac_coordinator import create_stac_coordinator_agent, STACSearchResult
from src.agents.response_synthesizer import create_response_synthesizer_agent
from src.utils.observability import setup_telemetry, traced_agent

setup_telemetry()


@traced_agent(
    "agent_1_query_parser", capture_args=["user_query"], capture_output="parsed_query"
)
async def run_query_parser(*, user_query: str) -> ParsedQuery:
    """Parse user query to extract intent, keywords, location, and datetime."""
    print(f"\n[Agent 1] Parsing user query: '{user_query}'...")
    query_parser = create_query_parser_agent()
    parsed_response = await query_parser.run(
        user_query, options={"response_format": ParsedQuery}
    )
    parsed_query = parsed_response.value

    assert isinstance(
        parsed_query, ParsedQuery
    ), "Expected ParsedQuery from query parser"

    print(f"  Intent: {parsed_query.intent}")
    if parsed_query.metadata_sub_intent:
        print(f"  Sub-Intent: {parsed_query.metadata_sub_intent}")
    print(f"  Keywords: {parsed_query.data_type_keywords}")
    print(f"  Location: {parsed_query.location}")
    print(f"  Datetime: {parsed_query.datetime}")

    return parsed_query


@traced_agent(
    "agent_2_geocoding",
    capture_args=["location", "datetime"],
    capture_output="geocoding_result",
)
async def run_geocoding_agent(
    *, location: Optional[str], datetime: Optional[str]
) -> GeocodingResult:
    """Resolve location to bounding box and datetime to ISO 8601 format."""
    print(f"\n[Agent 2] Resolving location and datetime...")
    geocoding_agent = create_geocoding_agent()
    geocoding_prompt = f"""
    Resolve the following location and datetime information:
    - Location: {location}
    - Datetime: {datetime}

    Use the geocode() function tool for location resolution.
    Convert datetime into ISO 8601 format.
    """
    geocoding_response = await geocoding_agent.run(
        geocoding_prompt, options={"response_format": GeocodingResult}
    )
    geocoding_result = geocoding_response.value

    assert isinstance(
        geocoding_result, GeocodingResult
    ), "Expected GeocodingResult from geocoding agent"

    print(f"  BBox: {geocoding_result.bbox}")
    print(f"  Resolved Datetime: {geocoding_result.datetime}")
    print(f"  Source: {geocoding_result.location_source}")

    return geocoding_result


@traced_agent(
    "agent_3_stac_coordinator",
    capture_args=["user_query", "intent", "collections", "bbox", "datetime"],
    capture_output="stac_result",
)
async def run_stac_agent(
    *,
    user_query: str,
    intent: str,
    metadata_sub_intent: Optional[str],
    collections: List[str],
    bbox: Optional[List[float]],
    datetime: Optional[str],
) -> STACSearchResult:
    """Search STAC catalogs based on intent and parameters."""
    print(f"\n[Agent 3] Running STAC Coordinator...")
    stac_agent = create_stac_coordinator_agent()

    # Build prompt based on intent
    if intent == "data_search":
        stac_prompt = f"""
        Search the STAC catalogs for actual data items:
        - Collections: {collections if collections else 'all'}
        - BBox: {bbox}
        - Datetime: {datetime}

        Use the search_and_summarize() function tool to find items.
        """
    elif intent == "metadata_query":
        stac_prompt = f"User query: {user_query}\n\n"

        if metadata_sub_intent == "list_collections":
            stac_prompt += "Use list_collections() to show all available collections."
        elif metadata_sub_intent == "collection_details":
            if collections:
                stac_prompt += f"Get details for these collections: {collections}\n"
                stac_prompt += "Use get_collection_details() for each collection ID."
            else:
                stac_prompt += (
                    "Use list_collections() since no specific data type was mentioned."
                )
        elif metadata_sub_intent == "count_items":
            if collections:
                stac_prompt += f"Count items in these collections: {collections}\n"
            else:
                stac_prompt += "Count items across all collections.\n"
            if bbox:
                stac_prompt += f"BBox: {bbox}\n"
            if datetime:
                stac_prompt += f"Datetime: {datetime}\n"
            stac_prompt += (
                "Use search_and_summarize() with limit=1000 to get accurate counts."
            )
        else:
            stac_prompt += "Use the appropriate function to answer the user's question."
    else:
        stac_prompt = f"User query: {user_query}\n\nProvide relevant information."

    stac_response = await stac_agent.run(
        stac_prompt, options={"response_format": STACSearchResult}
    )
    stac_search_result = stac_response.value

    assert isinstance(
        stac_search_result, STACSearchResult
    ), "Expected STACSearchResult from STAC agent"

    print(f"  Found {stac_search_result.count} items")
    print(f"  Date range: {stac_search_result.date_range}")
    print(f"  Collections: {stac_search_result.collections}")

    return stac_search_result


@traced_agent(
    "agent_4_response_synthesizer",
    capture_args=["user_query", "item_count", "date_range", "collections"],
    capture_output="final_response",
)
async def run_response_synthesizer(
    *,
    user_query: str,
    item_count: int,
    date_range: Optional[str],
    collections: List[str],
    sample_items: List[Any],
) -> str:
    """Synthesize a final response for the user based on search results."""
    print(f"\n[Agent 4] Synthesizing final response...")
    synthesizer = create_response_synthesizer_agent()
    synthesizer_prompt = f"""
    User asked: "{user_query}"

    Search Results:
    - Found {item_count} items
    - Date Range: {date_range}
    - Collections: {collections}
    - Sample Items: {sample_items[:10]}

    Generate a helpful response to the user query based on the search results.
    """
    final_response = await synthesizer.run(synthesizer_prompt)
    print(f"  Response Generated.")

    return final_response.text
