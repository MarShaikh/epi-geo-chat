"""
Agent runner functions for the multi-agent workflow.

Each function wraps an agent with observability tracing and handles
the execution logic for a specific step in the workflow pipeline.
"""

import asyncio
import json as _json
from typing import Any, Dict, List, Optional

from src.agents.code_generator import GeneratedCode, create_code_generator_agent
from src.rag.code_sample_retriever import retrieve_code_samples
from src.agents.geocoding_temporal import GeocodingResult, create_geocoding_agent
from src.agents.query_parser import ParsedQuery, create_query_parser_agent
from src.agents.response_synthesizer import create_response_synthesizer_agent
from src.agents.stac_coordinator import STACSearchResult, create_stac_coordinator_agent
from src.code_executor.models import AnalysisResult
from src.utils.observability import setup_telemetry, traced_agent

setup_telemetry()


@traced_agent(
    "query_parser", capture_args=["user_query"], capture_output="parsed_query"
)
async def run_query_parser(*, user_query: str) -> ParsedQuery:
    """Parse user query to extract intent, keywords, location, and datetime."""
    print(f"\n[Query Parser] Parsing user query: '{user_query}'...")
    query_parser = create_query_parser_agent()
    parsed_response = await query_parser.run(
        user_query, options={"response_format": ParsedQuery}
    )
    parsed_query = parsed_response.value

    assert isinstance(parsed_query, ParsedQuery), (
        "Expected ParsedQuery from query parser"
    )

    print(f"  Intent: {parsed_query.intent}")
    if parsed_query.metadata_sub_intent:
        print(f"  Sub-Intent: {parsed_query.metadata_sub_intent}")
    print(f"  Keywords: {parsed_query.data_type_keywords}")
    print(f"  Location: {parsed_query.location}")
    print(f"  Datetime: {parsed_query.datetime}")

    return parsed_query


@traced_agent(
    "geocoding",
    capture_args=["location", "datetime"],
    capture_output="geocoding_result",
)
async def run_geocoding_agent(
    *, location: Optional[str], datetime: Optional[str]
) -> GeocodingResult:
    """Resolve location to bounding box and datetime to ISO 8601 format."""
    print(f"\n[Geocoding] Resolving location and datetime...")
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

    assert isinstance(geocoding_result, GeocodingResult), (
        "Expected GeocodingResult from geocoding agent"
    )

    print(f"  BBox: {geocoding_result.bbox}")
    print(f"  Resolved Datetime: {geocoding_result.datetime}")
    print(f"  Source: {geocoding_result.location_source}")

    return geocoding_result


@traced_agent(
    "stac_coordinator",
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
    print(f"\n[STAC Coordinator] Running STAC search...")
    stac_agent = create_stac_coordinator_agent()

    # Build prompt — each branch tells the agent exactly which ONE tool to call
    if intent in ("data_search", "analysis"):
        stac_prompt = f"""
        Intent: {intent}
        Collections: {collections if collections else "all"}
        BBox: {bbox}
        Datetime: {datetime}

        Call search_and_summarize() ONCE with these parameters, then return the result.
        """
    elif intent == "metadata_query":
        if metadata_sub_intent == "list_collections":
            stac_prompt = "Call list_collections() ONCE, then return the result."
        elif metadata_sub_intent == "collection_details":
            if collections:
                # Only ask for the first collection to enforce single tool call
                stac_prompt = (
                    f"Call get_collection_details('{collections[0]}') ONCE, "
                    "then return the result."
                )
            else:
                stac_prompt = "Call list_collections() ONCE, then return the result."
        elif metadata_sub_intent == "count_items":
            stac_prompt = f"""
            Collections: {collections if collections else "all"}
            BBox: {bbox}
            Datetime: {datetime}

            Call search_and_summarize() ONCE with limit=1000, then return the result.
            """
        else:
            stac_prompt = (
                f"User query: {user_query}\n\n"
                "Pick the single most appropriate tool, call it ONCE, then return."
            )
    else:
        stac_prompt = (
            f"User query: {user_query}\n\n"
            "Pick the single most appropriate tool, call it ONCE, then return."
        )

    try:
        stac_response = await asyncio.wait_for(
            stac_agent.run(stac_prompt, options={"response_format": STACSearchResult}),
            timeout=30,
        )
        stac_search_result = stac_response.value
    except asyncio.TimeoutError:
        print("  [STAC Coordinator] Timed out after 30s — returning empty result")
        return STACSearchResult(
            count=0,
            collections=collections,
            date_range=datetime or "Unknown",
            items=[],
            bbox_searched=bbox,
            description="STAC search timed out",
        )

    assert isinstance(stac_search_result, STACSearchResult), (
        "Expected STACSearchResult from STAC agent"
    )

    print(f"  Found {stac_search_result.count} items")
    print(f"  Date range: {stac_search_result.date_range}")
    print(f"  Collections: {stac_search_result.collections}")

    return stac_search_result


@traced_agent(
    "response_synthesizer",
    capture_args=[
        "user_query",
        "intent",
        "metadata_sub_intent",
        "item_count",
        "date_range",
        "collections",
    ],
    capture_output="final_response",
)
async def run_response_synthesizer(
    *,
    user_query: str,
    intent: str,
    metadata_sub_intent: Optional[str],
    item_count: int,
    date_range: Optional[str],
    collections: List[str],
    sample_items: List[Any],
    analysis: Optional[AnalysisResult] = None,
) -> str:
    """Synthesize a final response for the user based on search results."""
    print(f"\n[Response Synthesizer] Synthesizing final response...")
    synthesizer = create_response_synthesizer_agent()
    synthesizer_prompt = f"""
    User asked: "{user_query}"

    Parameters from STAC including intent:
    - Found {item_count} items
    - Intent: {intent}
    - Metadata Sub-Intent: {metadata_sub_intent}
    - Date Range: {date_range}
    - Collections: {collections}
    - Sample Items: {sample_items[:10]}
    """

    if analysis:
        synthesizer_prompt += f"""
    Analysis execution results:
    - Description: {analysis.description}
    - Artifacts generated: {len(analysis.artifacts)} ({', '.join(a.filename for a in analysis.artifacts)})
    - Execution time: {analysis.execution_time_ms}ms
    - Success: {analysis.error is None}
    {"- Error: " + analysis.error if analysis.error else ""}

    Summarize the analysis results and mention the generated artifacts.
    """
    else:
        synthesizer_prompt += """
    Generate a helpful response to the user query based on these results.
    """

    final_response = await synthesizer.run(synthesizer_prompt)
    print(f"  Response Generated.")

    return final_response.text


@traced_agent(
    "code_generator",
    capture_args=["user_query"],
    capture_output="generated_code",
)
async def run_code_generator(
    *,
    user_query: str,
    stac_result: STACSearchResult,
    geocoding_result: GeocodingResult,
    collection_overviews: Optional[List[Dict[str, Any]]] = None,
) -> GeneratedCode:
    """Generate Python analysis code based on STAC search results.

    Note: STACSearchResult.items only contains summary info (id, datetime, asset keys).
    The full items with signed asset URLs are fetched separately in the workflow
    and passed to the Docker sandbox via data.json.
    """
    print(f"\n[Code Generator] Generating analysis code...")
    code_gen = create_code_generator_agent()

    # Retrieve relevant code examples to ground generation
    examples = retrieve_code_samples(user_query, n_results=3)
    if examples:
        print(f"  Retrieved {len(examples)} code sample(s) for RAG: {[e['filepath'] for e in examples]}")

    # Build collection context section
    collection_context = ""
    if collection_overviews:
        collection_context = "\n\n    DATA CONTEXT — what these collections contain:\n"
        for ov in collection_overviews:
            if "error" in ov:
                continue
            collection_context += f"""
    Collection: {ov['id']}
      Title: {ov.get('title', 'N/A')}
      Description: {ov.get('description', 'N/A')}
      Keywords: {', '.join(ov.get('keywords', []))}
      Providers: {', '.join(ov.get('providers', []))}"""
            if ov.get("item_assets"):
                collection_context += "\n      Assets per item:"
                for asset_key, asset_info in ov["item_assets"].items():
                    title = asset_info.get("title", "")
                    desc = asset_info.get("description", "")
                    atype = asset_info.get("type", "")
                    label = title or desc or atype
                    collection_context += f"\n        - {asset_key}: {label} ({atype})"
            if ov.get("summaries"):
                collection_context += f"\n      Summaries: {_json.dumps(ov['summaries'], default=str)[:500]}"
            collection_context += "\n"

    prompt = f"""
    User query: "{user_query}"

    Available data:
    - Collections: {stac_result.collections}
    - Item count: {stac_result.count}
    - Date range: {stac_result.date_range}
    - BBox searched: {geocoding_result.bbox}
    - Datetime: {geocoding_result.datetime}
    - Sample items (id, datetime, asset keys): {
        [
            {"id": item.id, "datetime": item.datetime, "assets": item.assets}
            for item in (stac_result.items or [])[:10]
        ]
    }
    {collection_context}
    Generate a Python script that answers the user's analysis query using this data.
    The script will receive the full item list (with signed asset URLs) in /workspace/input/data.json.
    Use the collection metadata above to understand what the data represents (units, bands, variable meanings).
    """

    if examples:
        prompt += "\n\nREFERENCE EXAMPLES — working code patterns to adapt (do not copy verbatim):\n"
        for i, ex in enumerate(examples, 1):
            prompt += f"\n--- Example {i}: {ex['filepath']} ---\n{ex['source']}\n"

    response = await code_gen.run(prompt, options={"response_format": GeneratedCode})
    generated = response.value

    assert isinstance(generated, GeneratedCode), (
        "Expected GeneratedCode from code generator"
    )

    print(f"  Description: {generated.description}")
    print(f"  Expected outputs: {generated.expected_output}")

    return generated
