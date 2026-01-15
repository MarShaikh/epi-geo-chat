"""
Multi-agent workflow with structured outputs for geospatial data querying and response generation.
"""

from typing import Dict, Any
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
            "parsed_query": self.parsed_query.model_dump(),
            "geocoding_result": self.geocoding_result.model_dump(),
            "stac_results": self.stac_search_result.model_dump(),
            "final_response": self.final_response,
        }


async def process_query(user_query: str) -> WorkflowResult:
    """
    Execute the full 4-agent workflow with structured outputs.

    This function chains the agents manually, passing validated Pydantic models between each step for type safety and reliability.

    Args:
        user_query (str): Natual Language query from the user.
    Returns:
        WorkflowResult: Containing all the intermediate and final results.

    Example:
        >>> result = await process_query("Show me rainfall for Lagos for February 2023.")
        >>> print(result.final_response)
        >>> print(f"Found {result.stac_results.count} items.)
    """
    # 1. Agent 1: Query Parser
    print(f"\n[Agent 1] Parsing user query: '{user_query}'...")
    query_parser = create_query_parser_agent()

    parsed_response = await query_parser.run(user_query, response_format=ParsedQuery)
    parsed_query = parsed_response.value
    assert isinstance(
        parsed_query, ParsedQuery
    ), "Expected ParsedQuery from query parser"

    print(f"Intent: {parsed_query.intent}")
    print(f"Keywords from user query: {parsed_query.data_type_keywords}")
    print(f"Location: {parsed_query.location}")
    print(f"Datetime: {parsed_query.datetime}")

    # resolve location using RAG
    collections = resolve_collections_by_keywords(
        data_type_keywords=parsed_query.data_type_keywords,
        limit=3,
    )

    print(f"RAG Resolved Collections: {collections}")

    # 2. Agent 2: Geocoding and Temporal Interpretation
    print(f"\n[Agent 2] Resolving location and datetime...")
    geocoding_agent = create_geocoding_agent()

    geocoding_prompt = f"""
    Resolve the following location and datetime information: 
    - Location: {parsed_query.location}
    - Datetime: {parsed_query.datetime}

    Use the geocode() function tool for the location resolution.
    Convert datetime into ISO 8601 format
    """

    geocoding_response = await geocoding_agent.run(
        geocoding_prompt, response_format=GeocodingResult
    )
    geocoding_result = geocoding_response.value
    assert isinstance(
        geocoding_result, GeocodingResult
    ), "Expected Geocoding Result from geocoding agent"

    print(f"BBox: {geocoding_result.bbox}")
    print(f"Resolved Datetime: {geocoding_result.datetime}")
    print(f"Source: {geocoding_result.location_source}")

    # 3. Agent 3. Search STAC Catalogs
    print(f"\n[Agent 3] Searching STAC catalogs...")
    stac_agent = create_stac_coordinator_agent()

    stac_prompt = f"""
    Search the STAC catalogs for the following: 
    - Collections: {collections[0]}
    - BBox: {geocoding_result.bbox}
    - Datetime: {geocoding_result.datetime}

    Use the search() function tool to perform the search.
    """

    stac_response = await stac_agent.run(stac_prompt, response_format=STACSearchResult)

    stac_search_result = stac_response.value
    assert isinstance(
        stac_search_result, STACSearchResult
    ), "Expected STACSearchResult from STAC agent"

    print(f"Found {stac_search_result.count} items.")
    print(f"Date ranges: {stac_search_result.date_range}")
    print(f"Collections searched: {stac_search_result.collections}")

    items = [item.id for item in stac_search_result.items]
    print(f"Items (up to 10): {items[:10]}")

    # 4. Agent 4: Synthesize Response
    print(f"\n[Agent 4] Synthesizing final response...")
    synthesizer = create_response_synthesizer_agent()

    synthesizer_prompt = f"""
    User asked: "{user_query}"

    Search Results: 
    - Found {stac_search_result.count} items
    - Date Range: {stac_search_result.date_range} 
    - Collections: {stac_search_result.collections}
    - Sample Items: {items[:10]}

    Generate Helpful response to user query based on the search results.
    """

    final_response = await synthesizer.run(synthesizer_prompt)
    print(f"Response Generated.")
    print(f"\n{'='*60}")
    print(f"Final Response")
    print(f"\n{'='*60}\n  {final_response.text}\n")
    print(f"\n{'='*60}")

    # return complete workflow result
    return WorkflowResult(
        user_query=user_query,
        parsed_query=parsed_query,
        geocoding_result=geocoding_result,
        stac_search_result=stac_search_result,
        final_response=final_response.text,
    )


async def process_query_silent(user_query: str) -> WorkflowResult:
    """
    Silent version of process_query without print statements for production use.
    """
    # 1. Agent 1: Query Parser
    query_parser = create_query_parser_agent()

    parsed_response = await query_parser.run(user_query, response_format=ParsedQuery)
    parsed_query = parsed_response.value
    assert isinstance(
        parsed_query, ParsedQuery
    ), "Expected ParsedQuery from query parser"

    # 2. Agent 2: Geocoding and Temporal Interpretation
    geocoding_agent = create_geocoding_agent()

    geocoding_prompt = f"""
    Resolve the following location and datetime information: 
    - Location: {parsed_query.location}
    - Datetime: {parsed_query.datetime}

    Use the geocode() function tool for the location resolution.
    Convert datetime into ISO 8601 format
    """

    geocoding_response = await geocoding_agent.run(
        geocoding_prompt, response_format=GeocodingResult
    )
    geocoding_result = geocoding_response.value
    assert isinstance(
        geocoding_result, GeocodingResult
    ), "Expected Geocoding Result from geocoding agent"

    # 3. Agent 3. Search STAC Catalogs
    stac_agent = create_stac_coordinator_agent()

    stac_prompt = f"""
    Search the STAC catalogs for the following: 
    - Collections: {parsed_query.collections}
    - BBox: {geocoding_result.bbox}
    - Datetime: {geocoding_result.datetime}

    Use the search() function tool to perform the search.
    """

    stac_response = await stac_agent.run(stac_prompt, response_format=STACSearchResult)

    stac_search_result = stac_response.value
    assert isinstance(
        stac_search_result, STACSearchResult
    ), "Expected STACSearchResult from STAC agent"

    # 4. Agent 4: Synthesize Response
    synthesizer = create_response_synthesizer_agent()

    synthesizer_prompt = f"""
    User asked: "{user_query}"

    Search Results: 
    - Found {stac_search_result.count} items
    - Date Range: {stac_search_result.date_range} 
    - Collections: {stac_search_result.collections}
    - Sample Items: {[item.id for item in stac_search_result.items]}

    Generate Helpful response to user query based on the search results.
    """

    final_response = await synthesizer.run(synthesizer_prompt)

    # return complete workflow result
    return WorkflowResult(
        user_query=user_query,
        parsed_query=parsed_query,
        geocoding_result=geocoding_result,
        stac_search_result=stac_search_result,
        final_response=final_response.text,
    )
