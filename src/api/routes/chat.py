"""Chat endpoints - core API for the agent workflow."""

import json
import traceback

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.api.schemas import ChatRequest, ChatResponse
from src.agents.workflow import AgentWorkflow

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Run the full agent workflow and return the complete result."""
    workflow = AgentWorkflow()
    try:
        result = await workflow.run(request.query)
        return ChatResponse.from_workflow_result(result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """SSE streaming endpoint that yields progress events as each agent completes."""

    async def event_generator():
        workflow = AgentWorkflow()
        try:
            async for event in workflow.run_streaming(request.query):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            error_event = {
                "event": "error",
                "message": str(e),
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
