"""
Multi-agent workflow with structured outputs for geospatial data querying and response generation.
"""
import os
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
            "parsed_query": self.parsed_query.model_dump() if self.parsed_query else None,
            "geocoding_result": self.geocoding_result.model_dump() if self.geocoding_result else None,
            "stac_results": self.stac_search_result.model_dump() if self.stac_search_result else None,
            "final_response": self.final_response,
        }
async def process_query(user_query: str) -> WorkflowResult:
    """
    Execute the multi-agent workflow with automatic intent-based routing.
    
    This function chains the agents manually, passing validated Pydantic models between each step for type safety and reliability.
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
    # Agent 1: Query Parsing

    print(f"\n[Agent 1] Parsing user query: '{user_query}'...")
    query_parser = create_query_parser_agent()
    
    parsed_response = await query_parser.run(user_query, options={"response_format": ParsedQuery })
    parsed_query = parsed_response.value
    
    assert isinstance(parsed_query, ParsedQuery), "Expected ParsedQuery from query parser"
    
    print(f"  Intent: {parsed_query.intent}")
    
    if parsed_query.metadata_sub_intent:
        print(f"  Sub-Intent: {parsed_query.metadata_sub_intent}")
    
    print(f"  Keywords: {parsed_query.data_type_keywords}")
    print(f"  Location: {parsed_query.location}")
    print(f"  Datetime: {parsed_query.datetime}")
    
    # Resolve collection if keywords are provided using RAG
    collections = []
    if parsed_query.data_type_keywords:
        collections = resolve_collections_by_keywords(
            data_type_keywords=parsed_query.data_type_keywords,
            limit=len(parsed_query.data_type_keywords)
        )
        print(f"[RAG] Resolved Collections: {collections}")
    
    # Agent 2: Geocoding & Temporal Resolution
    # Skip for certain metadata queries that don't need location
    
    geocoding_result = None
    
    # Only geocode if we have location/datetime OR if it's a data_search
    if parsed_query.location or parsed_query.datetime or parsed_query.intent == "data_search":
        print(f"\n[Agent 2] Resolving location and datetime...")
        geocoding_agent = create_geocoding_agent()
        geocoding_prompt = f"""
        Resolve the following location and datetime information:
        - Location: {parsed_query.location}
        - Datetime: {parsed_query.datetime}
        
        Use the geocode() function tool for location resolution.
        Convert datetime into ISO 8601 format.
        """
        geocoding_response = await geocoding_agent.run(
            geocoding_prompt, options={"response_format": GeocodingResult }
        )
        geocoding_result = geocoding_response.value
        
        assert isinstance(geocoding_result, GeocodingResult), "Expected GeocodingResult from geocoding agent"
        
        print(f"  BBox: {geocoding_result.bbox}")
        print(f"  Resolved Datetime: {geocoding_result.datetime}")
        print(f"  Source: {geocoding_result.location_source}")
    
    else:
        # Create empty geocoding result for metadata queries without location
        geocoding_result = GeocodingResult(
            bbox=None,
            datetime=None,
            location_source="not_applicable"
        )
    
    
    # Agent 3: STAC Coordinator
    # Builds different prompts based on intent

    print(f"\n[Agent 3] Running STAC Coordinator...")
    stac_agent = create_stac_coordinator_agent()
    
    # Build prompt based on intent
    if parsed_query.intent == "data_search":
        # Data search: Use search_and_summarize
        stac_prompt = f"""
        Search the STAC catalogs for actual data items:
        - Collections: {collections[0] if collections else 'all'}
        - BBox: {geocoding_result.bbox}
        - Datetime: {geocoding_result.datetime}
        
        Use the search_and_summarize() function tool to find items.
        """
    elif parsed_query.intent == "metadata_query":
        
        # Metadata query: Route based on sub-intent
        stac_prompt = f"User query: {user_query}\n\n"
        
        if parsed_query.metadata_sub_intent == "list_collections":
            stac_prompt += "Use list_collections() to show all available collections."
        
        elif parsed_query.metadata_sub_intent == "collection_details":
            if collections:
                stac_prompt += f"Get details for these collections: {collections}\n"
                stac_prompt += "Use get_collection_details() for each collection ID."
            else:
                stac_prompt += "Use list_collections() since no specific data type was mentioned."
        
        elif parsed_query.metadata_sub_intent == "count_items":
            if collections:
                stac_prompt += f"Count items in these collections: {collections}\n"
            else:
                stac_prompt += "Count items across all collections.\n"
            
            if geocoding_result.bbox:
                stac_prompt += f"BBox: {geocoding_result.bbox}\n"
            if geocoding_result.datetime:
                stac_prompt += f"Datetime: {geocoding_result.datetime}\n"
            stac_prompt += "Use search_and_summarize() with limit=1000 to get accurate counts."
        
        else:
            # Generic metadata query
            stac_prompt += "Use the appropriate function to answer the user's question."
    else:
        # Fallback for chat/analysis intents
        stac_prompt = f"User query: {user_query}\n\nProvide relevant information."
    
    # Run STAC agent
    stac_response = await stac_agent.run(stac_prompt, options={"response_format": STACSearchResult })
    stac_search_result = stac_response.value
    
    assert isinstance(stac_search_result, STACSearchResult), "Expected STACSearchResult from STAC agent"
        
    print(f"  Found {stac_search_result.count} items")
    print(f"  Date range: {stac_search_result.date_range}")
    print(f"  Collections: {stac_search_result.collections}")
    
    # Agent 4: Response Synthesis
    print(f"\n[Agent 4] Synthesizing final response...")
    synthesizer = create_response_synthesizer_agent()
    synthesizer_prompt = f"""
    User asked: "{user_query}"
    
    Search Results:
    - Found {stac_search_result.count} items
    - Date Range: {stac_search_result.date_range}
    - Collections: {stac_search_result.collections}
    - Sample Items: {stac_search_result.items[:10]}
    
    Generate a helpful response to the user query based on the search results.
    """
    final_response = await synthesizer.run(synthesizer_prompt)
    print(f"  Response Generated.")
    
    print(f"\n{'='*60}")
    print(f"Final Response")
    print(f"\n{'='*60}\n  {final_response.text}\n")
    print(f"\n{'='*60}")
    
    return WorkflowResult(
        user_query=user_query,
        parsed_query=parsed_query,
        geocoding_result=geocoding_result,
        stac_search_result=stac_search_result,
        final_response=final_response.text,
    )