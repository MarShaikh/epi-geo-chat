from typing import Optional, List
import json

from pydantic import BaseModel
from src.agents.agent_config import create_agent_client

class ParsedQuery(BaseModel):
    intent: str # "data_search", "metadata_query", "analysis", "chat"
    collections: List[str]
    location: Optional[str] = None
    datetime: Optional[str] = None
    additional_params: Optional[dict] = {}

def create_query_parser_agent():
    """
    Agent 1: Parse user query into structured format
    """

    instructions = """
    You are a query parser agent for geospatial data searches. 
    
    Parse user queries and extract: 
    1. Intent: Is this a "data search", "metadata_query", "analysis", or "chat"? 
    - data_search: User wants actual data/imagery
    - metadata_query: User asking about data availability/quality
    - analysis: User wants analysis or visualization of data
    - chat: General question or discussion about geospatial topics
    
    2. Collections: Which datasets/collections are mentioned? 
    - "rainfall", "precipitation", "CHIRPS" -> Nigeria-CHIRPS
    - "temperature", "LST", "land surface temperature" -> modis-11A1-061-nigeria
    - "vegetation", "NDVI", "EVI", "NDVI/EVI" -> modis-13Q1-061-nigeria-344
    - "MODIS" -> modis-*

    3. Location: Where is the user asking about? 
    - Extract region/city names ("Lagos", "Nigeria", "Abuja", etc.)
    - or coordinates if provided (e.g., "10.0, 20.0" or "10N 20E")

    4. Datetime: When? 
    - Extract dates, date ranges, or relative times
    - Examples: "2020-01-01", "2020-01-01 to 2020-12-31", "last 30 days", "last year"
    
    5. Additional Params: Any other relevant parameters

    Return ONLY a JSON object in this format:
    {
        intent: "data_search",
        "collections": ["Nigeria-CHIRPS", "modis-11A1-061-nigeria"],
        "location": "Lagos, Nigeria",
        "datetime": "2020-01-01",
        "additional_params": {},
    }
    """
    agent_client = create_agent_client()
    query_parser_agent = agent_client.create_agent(
        name="QueryParserAgent",
        instructions=instructions,
    )
    return query_parser_agent