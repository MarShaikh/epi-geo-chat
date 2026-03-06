"""Tests for src.code_executor.models — Pydantic model validation."""

import pytest
from pydantic import ValidationError

from src.code_executor.models import AnalysisArtifact, AnalysisResult


class TestAnalysisArtifact:

    def test_valid_artifact(self):
        artifact = AnalysisArtifact(
            artifact_id="abc-123",
            filename="plot.png",
            content_type="image/png",
            size_bytes=1024,
        )
        assert artifact.artifact_id == "abc-123"
        assert artifact.filename == "plot.png"
        assert artifact.content_type == "image/png"
        assert artifact.size_bytes == 1024

    def test_missing_required_field(self):
        with pytest.raises(ValidationError):
            AnalysisArtifact(
                artifact_id="abc-123",
                filename="plot.png",
                content_type="image/png",
                # missing size_bytes
            )

    def test_serialization_round_trip(self):
        artifact = AnalysisArtifact(
            artifact_id="abc-123",
            filename="plot.png",
            content_type="image/png",
            size_bytes=1024,
        )
        data = artifact.model_dump()
        restored = AnalysisArtifact(**data)
        assert restored == artifact


class TestAnalysisResult:

    def test_minimal_result(self):
        result = AnalysisResult(code="print('hi')", description="test")
        assert result.code == "print('hi')"
        assert result.description == "test"
        assert result.artifacts == []
        assert result.stdout == ""
        assert result.stderr == ""
        assert result.execution_time_ms == 0
        assert result.error is None

    def test_full_result(self):
        artifact = AnalysisArtifact(
            artifact_id="abc-123",
            filename="plot.png",
            content_type="image/png",
            size_bytes=2048,
        )
        result = AnalysisResult(
            code="import numpy",
            description="analysis",
            artifacts=[artifact],
            stdout="output line",
            stderr="warning",
            execution_time_ms=500,
            error=None,
        )
        assert len(result.artifacts) == 1
        assert result.execution_time_ms == 500

    def test_result_with_error(self):
        result = AnalysisResult(
            code="bad code",
            description="failed",
            error="SyntaxError: invalid syntax",
        )
        assert result.error == "SyntaxError: invalid syntax"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            AnalysisResult(code="print('hi')")  # missing description

    def test_serialization_round_trip(self):
        result = AnalysisResult(
            code="x = 1",
            description="test",
            artifacts=[
                AnalysisArtifact(
                    artifact_id="id1",
                    filename="f.csv",
                    content_type="text/csv",
                    size_bytes=100,
                )
            ],
            stdout="done",
            execution_time_ms=42,
        )
        data = result.model_dump()
        restored = AnalysisResult(**data)
        assert restored == result
