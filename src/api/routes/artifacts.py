"""Artifact serving endpoint for code execution outputs."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from src.code_executor.artifact_store import ArtifactStore

router = APIRouter(prefix="/artifacts", tags=["artifacts"])

_store = ArtifactStore()


@router.get("/{artifact_id}")
async def get_artifact(artifact_id: str):
    """Serve a generated artifact (PNG, HTML, CSV) by its ID."""
    result = _store.get(artifact_id)
    if not result:
        raise HTTPException(status_code=404, detail="Artifact not found or expired")
    path, content_type, filename = result
    return FileResponse(path, media_type=content_type, filename=filename)
