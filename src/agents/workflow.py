"""
Multi-agent workflow with structured outputs for geospatial data querying and response generation.
"""
from typing import Dict, Any, List, Optional
from src.agents.query_parser import create_query_parser_agent, ParsedQuery
from src.agents.geocoding_temporal import create_geocoding_agent, GeocodingResult
from src.agents.stac_coordinator import create_stac_coordinator_agent, STACSearchResult
from src.agents.response_synthesizer import create_response_synthesizer_agent
from src.rag.collection_resolver import resolve_collections_by_keywords

class WorkflowResult:
    """Class for the complete workflow results."""
    def __init__(
        self,
        user_query: str,
        parsed_query: ParsedQuery,
        geocoding_result: GeocodingResult,
        stac_search_result: STACSearchResult,
        final_response: str,
    ):
        self.user_query = user_query
        self.parsed_query = parsed_query
        self.geocoding_result = geocoding_result
        self.stac_search_result = stac_search_result
        self.final_response = final_response

    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow result into a dictionary for serialization."""
        return {
            "user_query": self.user_query,
            "parsed_query": self.parsed_query.model_dump() if self.parsed_query else None,
            "geocoding_result": self.geocoding_result.model_dump() if self.geocoding_result else None,
            "stac_results": self.stac_search_result.model_dump() if self.stac_search_result else None,
            "final_response": self.final_response,
        }

# set up observability
from src.utils.observability import setup_telemetry, traced, traced_agent
from opentelemetry.trace import SpanKind
from opentelemetry.trace import get_current_span
from opentelemetry.trace.span import format_trace_id

setup_telemetry()


# Agent 1: Query Parser
@traced_agent("agent_1_query_parser", capture_args=["user_query"], capture_output="parsed_query")
async def run_query_parser(*, user_query: str) -> ParsedQuery:
    """Parse user query to extract intent, keywords, location, and datetime."""
    print(f"\n[Agent 1] Parsing user query: '{user_query}'...")
    query_parser = create_query_parser_agent()
    parsed_response = await query_parser.run(user_query, options={"response_format": ParsedQuery})
    parsed_query = parsed_response.value

    assert isinstance(parsed_query, ParsedQuery), "Expected ParsedQuery from query parser"

    print(f"  Intent: {parsed_query.intent}")
    if parsed_query.metadata_sub_intent:
        print(f"  Sub-Intent: {parsed_query.metadata_sub_intent}")
    print(f"  Keywords: {parsed_query.data_type_keywords}")
    print(f"  Location: {parsed_query.location}")
    print(f"  Datetime: {parsed_query.datetime}")

    return parsed_query


# Agent 2: Geocoding & Temporal Resolution
@traced_agent("agent_2_geocoding", capture_args=["location", "datetime"], capture_output="geocoding_result")
async def run_geocoding_agent(*, location: Optional[str], datetime: Optional[str]) -> GeocodingResult:
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

    assert isinstance(geocoding_result, GeocodingResult), "Expected GeocodingResult from geocoding agent"

    print(f"  BBox: {geocoding_result.bbox}")
    print(f"  Resolved Datetime: {geocoding_result.datetime}")
    print(f"  Source: {geocoding_result.location_source}")

    return geocoding_result


# Agent 3: STAC Coordinator
@traced_agent(
    "agent_3_stac_coordinator",
    capture_args=["user_query", "intent", "collections", "bbox", "datetime"],
    capture_output="stac_result"
)
async def run_stac_agent(
    *,
    user_query: str,
    intent: str,
    metadata_sub_intent: Optional[str],
    collections: List[str],
    bbox: Optional[List[float]],
    datetime: Optional[str]
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
                stac_prompt += "Use list_collections() since no specific data type was mentioned."
        elif metadata_sub_intent == "count_items":
            if collections:
                stac_prompt += f"Count items in these collections: {collections}\n"
            else:
                stac_prompt += "Count items across all collections.\n"
            if bbox:
                stac_prompt += f"BBox: {bbox}\n"
            if datetime:
                stac_prompt += f"Datetime: {datetime}\n"
            stac_prompt += "Use search_and_summarize() with limit=1000 to get accurate counts."
        else:
            stac_prompt += "Use the appropriate function to answer the user's question."
    else:
        stac_prompt = f"User query: {user_query}\n\nProvide relevant information."

    stac_response = await stac_agent.run(stac_prompt, options={"response_format": STACSearchResult})
    stac_search_result = stac_response.value

    assert isinstance(stac_search_result, STACSearchResult), "Expected STACSearchResult from STAC agent"

    print(f"  Found {stac_search_result.count} items")
    print(f"  Date range: {stac_search_result.date_range}")
    print(f"  Collections: {stac_search_result.collections}")

    return stac_search_result


# Agent 4: Response Synthesizer
@traced_agent(
    "agent_4_response_synthesizer",
    capture_args=["user_query", "item_count", "date_range", "collections"],
    capture_output="final_response"
)
async def run_response_synthesizer(
    *,
    user_query: str,
    item_count: int,
    date_range: Optional[str],
    collections: List[str],
    sample_items: List[Any]
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


@traced("Multi-Agent Workflow Execution", kind=SpanKind.CLIENT)
async def process_query(user_query: str) -> WorkflowResult:
    """
    Execute the multi-agent workflow with automatic intent-based routing.

    This function chains the agents manually, passing validated Pydantic models
    between each step for type safety and reliability.
    1. Parses the query (Agent 1)
    2. Routes based on intent (data_search vs metadata_query)
    3. Executes appropriate pipeline
    4. Returns unified WorkflowResult

    Args:
        user_query (str): Natural language query from user

    Returns:
        WorkflowResult: Complete results including parsed query, geocoding, STAC results, and final response

    Examples:
        >>> result = await process_query("Show me rainfall for Lagos in February 2024")  # data_search
        >>> result = await process_query("What collections do we have?")  # metadata_query
    """
    current_span = get_current_span()
    print(f"Trace ID: {format_trace_id(current_span.get_span_context().trace_id)}")

    # Agent 1: Query Parsing
    parsed_query = await run_query_parser(user_query=user_query)

    # Resolve collection if keywords are provided using RAG
    collections = []
    if parsed_query.data_type_keywords:
        collections = resolve_collections_by_keywords(
            data_type_keywords=parsed_query.data_type_keywords,
            limit=len(parsed_query.data_type_keywords)
        )
        print(f"[RAG] Resolved Collections: {collections}")

    # Agent 2: Geocoding & Temporal Resolution
    # Only geocode if we have location/datetime OR if it's a data_search
    if parsed_query.location or parsed_query.datetime or parsed_query.intent == "data_search":
        geocoding_result = await run_geocoding_agent(
            location=parsed_query.location,
            datetime=parsed_query.datetime
        )
    else:
        # Create empty geocoding result for metadata queries without location
        geocoding_result = GeocodingResult(
            bbox=None,
            datetime=None,
            location_source="not_applicable"
        )

    # Agent 3: STAC Coordinator
    stac_search_result = await run_stac_agent(
        user_query=user_query,
        intent=parsed_query.intent,
        metadata_sub_intent=parsed_query.metadata_sub_intent,
        collections=collections,
        bbox=geocoding_result.bbox,
        datetime=geocoding_result.datetime
    )

    # Agent 4: Response Synthesis
    final_response = await run_response_synthesizer(
        user_query=user_query,
        item_count=stac_search_result.count or 0,
        date_range=stac_search_result.date_range,
        collections=stac_search_result.collections,
        sample_items=stac_search_result.items or []
    )

    print(f"\n{'='*60}")
    print(f"Final Response")
    print(f"\n{'='*60}\n  {final_response}\n")
    print(f"\n{'='*60}")

    return WorkflowResult(
        user_query=user_query,
        parsed_query=parsed_query,
        geocoding_result=geocoding_result,
        stac_search_result=stac_search_result,
        final_response=final_response,
    )
