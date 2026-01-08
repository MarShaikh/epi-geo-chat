from src.agents.agent_config import create_agent_client
from src.stac.catalog_client import GeoCatalogClient

def create_stac_coordinator_agent():
    """
    Agent 3: Execute STAC catalog searches and optimize results. This agent with the STAC API to search for data.
    """

    instructions = """
    You are a STAC (SpatioTemporal Asset Catalog) coordinator agent for geospatial data queries.

    Your responsibilities include:
    1. Take parsed query parameters (collections, bbox, datetime) 
    2. Execute STAC API searches
    3. Optimize and filter results
    4. Return a summary of findings

    When you receive search parameters, you will execute the search and provide a summary including:
    - Number of items found 
    - Date range of covered
    - Available data assets (COG files, metadata, etc.)
    - Quality of information if available

    Return results in JSON format:
    {
        "count": <number_of_items>, 
        "collections": [<collection_ids>],
        "date_range": "<range>"},
        "items": [<summary_of_items>]
    }
    """
    catalog_client = GeoCatalogClient()
    agent_client = create_agent_client()
    catalog_agent = agent_client.create_agent(
        name="STACCoordinatorAgent",
        instructions=instructions,
        tools=catalog_client.search
    )
    return catalog_agent