"""
Multi-agent workflow orchestration for geospatial data querying.
"""

from typing import AsyncGenerator, Dict, Any, List, Optional

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
    run_code_generator,
)
from src.rag.collection_resolver import resolve_collections_by_keywords
from src.stac.catalog_client import GeoCatalogClient
from src.code_executor.validator import CodeValidator
from src.code_executor.sandbox import DockerSandbox
from src.code_executor.artifact_store import ArtifactStore
from src.code_executor.models import AnalysisResult, AnalysisArtifact
from src.utils.observability import traced

# Shared instances for code execution
_artifact_store = ArtifactStore()
_code_validator = CodeValidator()


class WorkflowResult:
    """Class for the complete workflow results."""

    def __init__(
        self,
        user_query: str,
        parsed_query: ParsedQuery,
        geocoding_result: GeocodingResult,
        stac_search_result: STACSearchResult,
        final_response: str,
        analysis: Optional[AnalysisResult] = None,
    ):
        self.user_query = user_query
        self.parsed_query = parsed_query
        self.geocoding_result = geocoding_result
        self.stac_search_result = stac_search_result
        self.final_response = final_response
        self.analysis = analysis

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
            "analysis": (
                self.analysis.model_dump() if self.analysis else None
            ),
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
            "code_generator": run_code_generator,
        }

    @traced("AgentWorkflow.run", kind=SpanKind.CLIENT)
    async def run(self, user_query: str) -> WorkflowResult:
        """
        Execute the multi-agent workflow with automatic intent-based routing.

        Chains agents sequentially, passing validated Pydantic models between
        each step for type safety:
        - Parses the query
        - Resolves location and datetime
        - Searches STAC catalogs
        - Runs code execution (analysis intent only)
        - Synthesizes final response (always last)

        Args:
            user_query: Natural language query from user

        Returns:
            WorkflowResult: Complete results including parsed query, geocoding,
                          STAC results, and final response
        """
        current_span = get_current_span()
        print(f"Trace ID: {format_trace_id(current_span.get_span_context().trace_id)}")

        # Query Parsing
        parsed_query = await self.agents["query_parser"](user_query=user_query)

        # Resolve collection if keywords are provided using RAG
        collections: List[str] = []
        if parsed_query.data_type_keywords:
            collections = resolve_collections_by_keywords(
                data_type_keywords=parsed_query.data_type_keywords,
                limit=len(parsed_query.data_type_keywords),
            )

            print(f"[RAG] Resolved Collections: {collections}")

        # Geocoding & Temporal Resolution
        if (
            parsed_query.location
            or parsed_query.datetime
            or parsed_query.intent in ("data_search", "analysis")
        ):
            geocoding_result = await self.agents["geocoding"](
                location=parsed_query.location, datetime=parsed_query.datetime
            )
        else:
            geocoding_result = GeocodingResult(
                bbox=None, datetime=None, location_source="not_applicable"
            )

        if parsed_query.intent not in ["data_search", "metadata_query", "analysis"]:
            print(f"\n[STAC Coordinator] Skipping STAC search for intent: {parsed_query.intent}")
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
            # STAC Coordinator
            stac_search_result = await self.agents["stac_coordinator"](
                user_query=user_query,
                intent=parsed_query.intent,
                metadata_sub_intent=parsed_query.metadata_sub_intent,
                collections=collections,
                bbox=geocoding_result.bbox,
                datetime=geocoding_result.datetime,
            )

        # Code Generation & Execution (analysis intent only — runs before synthesis)
        analysis = None
        if (
            parsed_query.intent == "analysis"
            and stac_search_result.count
            and stac_search_result.count > 0
        ):
            analysis = await self._run_code_execution(
                user_query=user_query,
                stac_search_result=stac_search_result,
                geocoding_result=geocoding_result,
                collections=collections,
            )

        # Response Synthesis
        final_response = await self.agents["response_synthesizer"](
            user_query=user_query,
            intent=parsed_query.intent,
            metadata_sub_intent=parsed_query.metadata_sub_intent,
            item_count=stac_search_result.count or 0,
            date_range=stac_search_result.date_range,
            collections=stac_search_result.collections,
            sample_items=stac_search_result.items or [],
            analysis=analysis,
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
            analysis=analysis,
        )

    async def _run_code_execution(
        self,
        user_query: str,
        stac_search_result: STACSearchResult,
        geocoding_result: GeocodingResult,
        collections: List[str],
    ) -> AnalysisResult:
        """Run step 5: code generation, validation, and sandboxed execution.

        Re-fetches full STAC items (with signed asset URLs) from GeoCatalog
        since STACSearchResult.items only contains summaries.
        """
        import asyncio

        # 5a: Fetch collection metadata to give the code generator data context
        collection_overviews = await self._fetch_collection_overviews(collections)

        # 5b: Generate code
        generated = await self.agents["code_generator"](
            user_query=user_query,
            stac_result=stac_search_result,
            geocoding_result=geocoding_result,
            collection_overviews=collection_overviews,
        )

        # 5c: Validate code
        validation = _code_validator.validate(generated.code)
        if not validation.is_safe:
            print(f"[Code Executor] Code validation failed: {validation.violations}")
            return AnalysisResult(
                code=generated.code,
                description=generated.description,
                error=f"Code validation failed: {'; '.join(validation.violations)}",
            )

        # 5d: Re-fetch full items with signed asset URLs from GeoCatalog
        print("[Code Executor] Fetching full STAC items with signed asset URLs...")
        catalog_client = GeoCatalogClient()
        raw_results = await asyncio.to_thread(
            catalog_client.search,
            bbox=geocoding_result.bbox,
            datetime=geocoding_result.datetime,
            collections=collections,
            limit=stac_search_result.count or 20,
        )
        full_items = raw_results.get("features", [])

        # 5e: Build input data for sandbox
        input_data = {
            "user_query": user_query,
            "bbox": geocoding_result.bbox,
            "datetime": geocoding_result.datetime,
            "collections": collections,
            "items": [
                {
                    "id": item["id"],
                    "datetime": item.get("properties", {}).get("datetime"),
                    "assets": {
                        k: {"href": v.get("href", ""), "type": v.get("type", "")}
                        for k, v in item.get("assets", {}).items()
                    },
                    "bbox": item.get("bbox"),
                    "properties": item.get("properties", {}),
                }
                for item in full_items
            ],
        }

        # 5f: Execute in Docker sandbox
        print(f"[Code Executor] Executing code in sandbox ({len(full_items)} items)...")
        sandbox = DockerSandbox(_artifact_store)
        exec_result = await sandbox.execute(generated.code, input_data)

        print(f"[Code Executor] Execution {'succeeded' if exec_result.success else 'failed'} "
              f"in {exec_result.execution_time_ms}ms, {len(exec_result.artifacts)} artifacts")

        return AnalysisResult(
            code=generated.code,
            description=generated.description,
            artifacts=[
                AnalysisArtifact(
                    artifact_id=a.artifact_id,
                    filename=a.filename,
                    content_type=a.content_type,
                    size_bytes=a.size_bytes,
                )
                for a in exec_result.artifacts
            ],
            stdout=exec_result.stdout,
            stderr=exec_result.stderr,
            execution_time_ms=exec_result.execution_time_ms,
            error=exec_result.error,
        )

    async def _fetch_collection_overviews(
        self, collections: List[str]
    ) -> List[Dict[str, Any]]:
        """Fetch concise metadata for each collection to give the code generator data context.

        Returns a list of dicts with: id, description, keywords, providers.
        """
        import asyncio

        if not collections:
            return []

        catalog_client = GeoCatalogClient()
        overviews = []
        for coll_id in collections:
            try:
                coll_info = await asyncio.to_thread(
                    catalog_client.get_collection, coll_id
                )
                overviews.append({
                    "id": coll_id,
                    "title": coll_info.get("title", ""),
                    "description": coll_info.get("description", ""),
                    "keywords": coll_info.get("keywords", []),
                    "license": coll_info.get("license", ""),
                    "providers": [
                        p.get("name", "") for p in coll_info.get("providers", [])
                    ],
                    "summaries": coll_info.get("summaries", {}),
                    "item_assets": {
                        k: {
                            "title": v.get("title", ""),
                            "type": v.get("type", ""),
                            "description": v.get("description", ""),
                        }
                        for k, v in coll_info.get("item_assets", {}).items()
                    },
                })
            except Exception as e:
                print(f"[Workflow] Could not fetch metadata for {coll_id}: {e}")
                overviews.append({"id": coll_id, "error": str(e)})

        print(f"[Workflow] Fetched metadata for {len(overviews)} collection(s)")
        return overviews

    async def run_streaming(self, user_query: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute the workflow and yield SSE-compatible events after each agent step.

        Yields dicts with: event, agent, step, data, message fields.
        """
        # Query Parsing
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
            print(f"[RAG] Keywords: {parsed_query.data_type_keywords}")
            collections = resolve_collections_by_keywords(
                data_type_keywords=parsed_query.data_type_keywords,
                limit=len(parsed_query.data_type_keywords),
            )
            print(f"[RAG] Resolved Collections: {collections}")

        # Geocoding & Temporal Resolution
        yield {"event": "agent_started", "agent": "geocoding", "step": 2}
        if (
            parsed_query.location
            or parsed_query.datetime
            or parsed_query.intent in ("data_search", "analysis")
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

        # STAC Coordinator
        yield {"event": "agent_started", "agent": "stac_coordinator", "step": 3}
        if parsed_query.intent not in ["data_search", "metadata_query", "analysis"]:
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

        # Code Generation & Execution (analysis intent only — runs before synthesis)
        analysis = None
        if (
            parsed_query.intent == "analysis"
            and stac_search_result.count
            and stac_search_result.count > 0
        ):
            yield {"event": "agent_started", "agent": "code_executor", "step": 4}
            analysis = await self._run_code_execution(
                user_query=user_query,
                stac_search_result=stac_search_result,
                geocoding_result=geocoding_result,
                collections=collections,
            )
            yield {
                "event": "agent_completed",
                "agent": "code_executor",
                "step": 4,
                "data": analysis.model_dump(),
            }

        # Response Synthesis (always last)
        step = 5 if analysis is not None else 4
        yield {"event": "agent_started", "agent": "response_synthesizer", "step": step}
        final_response = await self.agents["response_synthesizer"](
            user_query=user_query,
            intent=parsed_query.intent,
            metadata_sub_intent=parsed_query.metadata_sub_intent,
            item_count=stac_search_result.count or 0,
            date_range=stac_search_result.date_range,
            collections=stac_search_result.collections,
            sample_items=stac_search_result.items or [],
            analysis=analysis,
        )
        yield {
            "event": "agent_completed",
            "agent": "response_synthesizer",
            "step": step,
            "data": {"response": final_response},
        }

        # Final complete result
        result = WorkflowResult(
            user_query=user_query,
            parsed_query=parsed_query,
            geocoding_result=geocoding_result,
            stac_search_result=stac_search_result,
            final_response=final_response,
            analysis=analysis,
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
