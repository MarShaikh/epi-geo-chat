"""
Multi-agent workflow orchestration for geospatial data querying.
"""

from typing import AsyncGenerator, Dict, Any, List

from opentelemetry.trace import SpanKind, get_current_span
from opentelemetry.trace.span import format_trace_id

from src.agents.query_parser import ParsedQuery
from src.agents.geocoding_temporal import GeocodingResult
from src.agents.stac_coordinator import STACSearchResult
from src.agents.agent_runners import (
    run_query_parser,
    run_geocoding_agent,
    run_stac_agent,
    run_response_synthesizer,
)
from src.rag.collection_resolver import resolve_collections_by_keywords
from src.utils.observability import traced


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
            "parsed_query": (
                self.parsed_query.model_dump() if self.parsed_query else None
            ),
            "geocoding_result": (
                self.geocoding_result.model_dump() if self.geocoding_result else None
            ),
            "stac_results": (
                self.stac_search_result.model_dump()
                if self.stac_search_result
                else None
            ),
            "final_response": self.final_response,
        }


class AgentWorkflow:
    """
    Orchestrates the multi-agent workflow for geospatial data querying.

    This class uses composition to coordinate agent runner functions,
    following the orchestrator-worker pattern. Each agent maintains single
    responsibility while the workflow handles routing and data flow.

    Attributes:
        agents: Registry of agent runner functions used in the workflow.

    Example:
        >>> workflow = AgentWorkflow()
        >>> result = await workflow.run("Show me rainfall for Lagos in February 2024")
    """

    def __init__(self):
        """Initialize the workflow with the agent registry."""
        self.agents = {
            "query_parser": run_query_parser,
            "geocoding": run_geocoding_agent,
            "stac_coordinator": run_stac_agent,
            "response_synthesizer": run_response_synthesizer,
        }

    @traced("AgentWorkflow.run", kind=SpanKind.CLIENT)
    async def run(self, user_query: str) -> WorkflowResult:
        """
        Execute the multi-agent workflow with automatic intent-based routing.

        Chains agents sequentially, passing validated Pydantic models between
        each step for type safety:
        1. Parses the query (Agent 1)
        2. Routes based on intent (data_search vs metadata_query)
        3. Executes appropriate pipeline
        4. Returns unified WorkflowResult

        Args:
            user_query: Natural language query from user

        Returns:
            WorkflowResult: Complete results including parsed query, geocoding,
                          STAC results, and final response
        """
        current_span = get_current_span()
        print(f"Trace ID: {format_trace_id(current_span.get_span_context().trace_id)}")

        # Agent 1: Query Parsing
        parsed_query = await self.agents["query_parser"](user_query=user_query)

        # Resolve collection if keywords are provided using RAG
        collections: List[str] = []
        if parsed_query.data_type_keywords:
            collections = resolve_collections_by_keywords(
                data_type_keywords=parsed_query.data_type_keywords,
                limit=len(parsed_query.data_type_keywords),
            )
            print(f"[RAG] Resolved Collections: {collections}")

        # Agent 2: Geocoding & Temporal Resolution
        if (
            parsed_query.location
            or parsed_query.datetime
            or parsed_query.intent == "data_search"
        ):
            geocoding_result = await self.agents["geocoding"](
                location=parsed_query.location, datetime=parsed_query.datetime
            )
        else:
            geocoding_result = GeocodingResult(
                bbox=None, datetime=None, location_source="not_applicable"
            )

        if parsed_query.intent not in ["data_search", "metadata_query"]:
            print(f"\n[Agent 3] Skipping STAC search for intent: {parsed_query.intent}")
            stac_search_result = STACSearchResult(
                count=0,
                collections=collections,
                date_range="Not applicable",
                items=[],
                bbox_searched=[],
                description="STAC search not applicable for this intent",
                keywords=[],
                license=None,
            )
        else:
            # Agent 3: STAC Coordinator
            stac_search_result = await self.agents["stac_coordinator"](
                user_query=user_query,
                intent=parsed_query.intent,
                metadata_sub_intent=parsed_query.metadata_sub_intent,
                collections=collections,
                bbox=geocoding_result.bbox,
                datetime=geocoding_result.datetime,
            )

        # Agent 4: Response Synthesis
        final_response = await self.agents["response_synthesizer"](
            user_query=user_query,
            intent=parsed_query.intent,
            metadata_sub_intent=parsed_query.metadata_sub_intent,
            item_count=stac_search_result.count or 0,
            date_range=stac_search_result.date_range,
            collections=stac_search_result.collections,
            sample_items=stac_search_result.items or [],
        )

        print(f"\n{'='*60}")
        print("Final Response")
        print(f"\n{'='*60}\n  {final_response}\n")
        print(f"\n{'='*60}")

        return WorkflowResult(
            user_query=user_query,
            parsed_query=parsed_query,
            geocoding_result=geocoding_result,
            stac_search_result=stac_search_result,
            final_response=final_response,
        )


    async def run_streaming(self, user_query: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute the workflow and yield SSE-compatible events after each agent step.

        Yields dicts with: event, agent, step, data, message fields.
        """
        # Step 1: Query Parsing
        yield {"event": "agent_started", "agent": "query_parser", "step": 1}
        parsed_query = await self.agents["query_parser"](user_query=user_query)
        yield {
            "event": "agent_completed",
            "agent": "query_parser",
            "step": 1,
            "data": parsed_query.model_dump(),
        }

        # RAG collection resolution
        collections: List[str] = []
        if parsed_query.data_type_keywords:
            collections = resolve_collections_by_keywords(
                data_type_keywords=parsed_query.data_type_keywords,
                limit=len(parsed_query.data_type_keywords),
            )

        # Step 2: Geocoding & Temporal Resolution
        yield {"event": "agent_started", "agent": "geocoding", "step": 2}
        if (
            parsed_query.location
            or parsed_query.datetime
            or parsed_query.intent == "data_search"
        ):
            geocoding_result = await self.agents["geocoding"](
                location=parsed_query.location, datetime=parsed_query.datetime
            )
        else:
            geocoding_result = GeocodingResult(
                bbox=None, datetime=None, location_source="not_applicable"
            )
        yield {
            "event": "agent_completed",
            "agent": "geocoding",
            "step": 2,
            "data": geocoding_result.model_dump(),
        }

        # Step 3: STAC Coordinator
        yield {"event": "agent_started", "agent": "stac_coordinator", "step": 3}
        if parsed_query.intent not in ["data_search", "metadata_query"]:
            stac_search_result = STACSearchResult(
                count=0,
                collections=collections,
                date_range="Not applicable",
                items=[],
                bbox_searched=[],
                description="STAC search not applicable for this intent",
                keywords=[],
                license=None,
            )
        else:
            stac_search_result = await self.agents["stac_coordinator"](
                user_query=user_query,
                intent=parsed_query.intent,
                metadata_sub_intent=parsed_query.metadata_sub_intent,
                collections=collections,
                bbox=geocoding_result.bbox,
                datetime=geocoding_result.datetime,
            )
        yield {
            "event": "agent_completed",
            "agent": "stac_coordinator",
            "step": 3,
            "data": stac_search_result.model_dump(),
        }

        # Step 4: Response Synthesis
        yield {"event": "agent_started", "agent": "response_synthesizer", "step": 4}
        final_response = await self.agents["response_synthesizer"](
            user_query=user_query,
            intent=parsed_query.intent,
            metadata_sub_intent=parsed_query.metadata_sub_intent,
            item_count=stac_search_result.count or 0,
            date_range=stac_search_result.date_range,
            collections=stac_search_result.collections,
            sample_items=stac_search_result.items or [],
        )
        yield {
            "event": "agent_completed",
            "agent": "response_synthesizer",
            "step": 4,
            "data": {"response": final_response},
        }

        # Final complete result
        result = WorkflowResult(
            user_query=user_query,
            parsed_query=parsed_query,
            geocoding_result=geocoding_result,
            stac_search_result=stac_search_result,
            final_response=final_response,
        )
        yield {"event": "done", "data": result.to_dict()}


async def process_query(user_query: str) -> WorkflowResult:
    """
    Convenience function that executes the AgentWorkflow.

    This function is kept for backward compatibility. For new code,
    prefer using AgentWorkflow directly.

    Args:
        user_query: Natural language query from user

    Returns:
        WorkflowResult: Complete workflow results
    """
    workflow = AgentWorkflow()
    return await workflow.run(user_query)
