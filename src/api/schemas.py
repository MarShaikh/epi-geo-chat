"""API request and response schemas."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from src.agents.query_parser import ParsedQuery
from src.agents.geocoding_temporal import GeocodingResult
from src.agents.stac_coordinator import STACSearchResult
from src.code_executor.models import AnalysisResult  # noqa: F401 (re-exported)


class ChatRequest(BaseModel):
    """Request body for chat endpoints."""

    query: str = Field(..., min_length=1, max_length=1000, description="Natural language query")
    session_id: Optional[str] = Field(default=None, description="Optional session identifier")


class ChatResponse(BaseModel):
    """Complete chat response combining all agent outputs."""

    query: str
    parsed_query: ParsedQuery
    geocoding: GeocodingResult
    stac_results: STACSearchResult
    response: str
    analysis: Optional[AnalysisResult] = None
    trace_id: Optional[str] = None

    @classmethod
    def from_workflow_result(cls, result, trace_id: Optional[str] = None) -> "ChatResponse":
        """Convert a WorkflowResult into a ChatResponse."""
        return cls(
            query=result.user_query,
            parsed_query=result.parsed_query,
            geocoding=result.geocoding_result,
            stac_results=result.stac_search_result,
            response=result.final_response,
            analysis=result.analysis,
            trace_id=trace_id,
        )


class StreamEvent(BaseModel):
    """Server-Sent Event payload for streaming responses."""

    event: str  # "agent_started", "agent_completed", "error", "done"
    agent: Optional[str] = None
    step: Optional[int] = None
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
