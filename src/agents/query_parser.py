from typing import Optional, List, Annotated
from pydantic import BaseModel, Field
from src.agents.agent_config import create_agent_client


class ParsedQuery(BaseModel):
    """Structured output for parsed user queries."""

    intent: Annotated[str, Field(
        description="Type of query: data_search, metadata_query, analysis, or chat"
    )]
    metadata_sub_intent: Annotated[Optional[str], Field(
        default=None,
        description="For metadata_query intent, specify sub-intent: list_collections, collection_details or count_items",
    )]
    data_type_keywords: Annotated[List[str], Field(
        description="List of keywords mentioned in the query"
    )]
    location: Annotated[Optional[str], Field(
        default=None, description="Location name or coordinates mentioned in query"
    )]
    datetime: Annotated[Optional[str], Field(
        default=None,
        description="Temporal reference from query (date, range, or relative time)",
    )]
    additional_params: Annotated[Optional[str], Field(
        default=None, description="Any additional parameters or context"
    )]


def create_query_parser_agent():
    """
    Agent 1: Parse user query into structured format.

    Returns structured output using ParsedQuery Pydantic model for type safety
    and validation.
    """

    instructions = """
    You are a query parser agent for geospatial data searches.

    Parse user queries and extract:
    1. Intent: Classify as "data_search", "metadata_query", "analysis", or "chat"
       - **data_search**: User wants actual data items/imagery to download or use
       Examples: 
        - "Show me rainfall data for Lagos in February 2024"
        - "Get temperature data for Kano last month"
        - "I need vegetation imagery for Nigeria in 2023"
       
       - **metadata_query**: User asking about what's available in the catalog
        Examples: 
        - "What collections do we have?"
        - "What data is available for Kano in 2023?"
        - "How much rainfall data is available?"
        - "What do you know about vegetation data?"
        - "Tell me about the MODIS collections"

        For metadata_query, ALSO classify the metadata_subintent: 

        a) **list_collections**: User wants to see all available collections
          - "What collections do we have?"
          - "List all available datasets"
          - "Show me all data sources"
           
        b) **collection_details**: User wants details about specific data types
          - "What do you know about vegetation data?"
          - "Tell me about the MODIS temperature collections"
          - "Give me details on rainfall datasets"
           
        c) **count_items**: User wants to know how much data is available
          - "What data is available for Kano in 2023?"
          - "How much rainfall data is available for Lagos?"
          - "How many temperature items do we have?"

       
       - **analysis**: User wants analysis or visualization of data
       - **chat**: General question or discussion about geospatial topics

    2. Data type keywords: What types of data is the user interested in?
        - Examples: ["rainfall", "precipitation"], ["temperature", "LST", "thermal"], ["vegetation", "NDVI"]
        - If asking about a specific collection name, include that: ["MODIS", "CHIRPS"]
        - For general queries like "What collections do we have?", leave this empty: []

    3. Location: Where is the user asking about?
        - Extract region/city names ("Lagos", "Nigeria", "Kano", "Abuja", etc.)
        - Or coordinates if provided (e.g., "10.0, 20.0" or "10N 20E")
        - Leave as null if no location mentioned

    4. Datetime: When?
       - Extract dates, date ranges, or relative times
       - Examples: "2020-01-01", "2020-01-01 to 2020-12-31", "last 30 days", "last year"

    5. Additional Params: Any other relevant parameters

    Examples:
      
    Query: "Show me rainfall data for Lagos in February 2024"
    Output:
    {
      "intent": "data_search",
      "metadata_sub_intent": null,
      "data_type_keywords": ["rainfall"],
      "location": "Lagos",
      "datetime": "February 2024",
      "additional_params": null
    }
    
    Query: "What collections do we have?"
    Output:
    {
      "intent": "metadata_query",
      "metadata_sub_intent": "list_collections",
      "data_type_keywords": [],
      "location": null,
      "datetime": null,
      "additional_params": null
    }
    
    Query: "What data is available for Kano in 2023?"
    Output:
    {
      "intent": "metadata_query",
      "metadata_sub_intent": "count_items",
      "data_type_keywords": [],
      "location": "Kano",
      "datetime": "2023",
      "additional_params": null
    }
    
    Query: "What do you know about vegetation data?"
    Output:
    {
      "intent": "metadata_query",
      "metadata_sub_intent": "collection_details",
      "data_type_keywords": ["vegetation"],
      "location": null,
      "datetime": null,
      "additional_params": null
    }

    """

    agent_client = create_agent_client()
    query_parser_agent = agent_client.as_agent(
        name="QueryParserAgent",
        instructions=instructions
    )
    return query_parser_agent
