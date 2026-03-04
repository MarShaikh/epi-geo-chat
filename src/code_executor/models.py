"""Shared models for code execution results."""

from typing import List, Optional

from pydantic import BaseModel


class AnalysisArtifact(BaseModel):
    """A single artifact produced by code execution."""

    artifact_id: str
    filename: str
    content_type: str
    size_bytes: int


class AnalysisResult(BaseModel):
    """Result of the code generation and execution step."""

    code: str
    description: str
    artifacts: List[AnalysisArtifact] = []
    stdout: str = ""
    stderr: str = ""
    execution_time_ms: int = 0
    error: Optional[str] = None
