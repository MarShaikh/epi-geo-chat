"""Tests for src.code_executor.artifact_store — file-based artifact storage with TTL."""

import datetime
import json
import tempfile
from pathlib import Path

import pytest

from src.code_executor.artifact_store import ArtifactStore, ArtifactInfo, _CONTENT_TYPES


@pytest.fixture
def tmp_store(tmp_path):
    """Create an ArtifactStore backed by a temporary directory."""
    return ArtifactStore(base_dir=str(tmp_path), ttl_minutes=60)


@pytest.fixture
def sample_file(tmp_path):
    """Create a sample PNG file to store."""
    f = tmp_path / "input" / "plot.png"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(b"\x89PNG fake image data")
    return f


class TestStore:

    def test_store_returns_artifact_info(self, tmp_store, sample_file):
        info = tmp_store.store(sample_file)
        assert isinstance(info, ArtifactInfo)
        assert info.filename == "plot.png"
        assert info.content_type == "image/png"
        assert info.size_bytes > 0
        assert len(info.artifact_id) == 36  # UUID format

    def test_store_creates_artifact_and_meta_files(self, tmp_store, sample_file):
        info = tmp_store.store(sample_file)
        artifact_path = tmp_store.base_dir / f"{info.artifact_id}.png"
        meta_path = tmp_store.base_dir / f"{info.artifact_id}.meta"
        assert artifact_path.exists()
        assert meta_path.exists()

    def test_meta_file_contains_expected_keys(self, tmp_store, sample_file):
        info = tmp_store.store(sample_file)
        meta_path = tmp_store.base_dir / f"{info.artifact_id}.meta"
        meta = json.loads(meta_path.read_text())
        assert meta["content_type"] == "image/png"
        assert meta["filename"] == "plot.png"
        assert meta["suffix"] == ".png"
        assert "created_at" in meta

    def test_store_unknown_extension(self, tmp_path):
        store = ArtifactStore(base_dir=str(tmp_path / "store"), ttl_minutes=60)
        f = tmp_path / "data.xyz"
        f.write_bytes(b"unknown data")
        info = store.store(f)
        assert info.content_type == "application/octet-stream"


class TestGet:

    def test_get_existing_artifact(self, tmp_store, sample_file):
        info = tmp_store.store(sample_file)
        result = tmp_store.get(info.artifact_id)
        assert result is not None
        path, content_type, filename = result
        assert path.exists()
        assert content_type == "image/png"
        assert filename == "plot.png"

    def test_get_nonexistent_artifact(self, tmp_store):
        result = tmp_store.get("nonexistent-uuid")
        assert result is None

    def test_get_expired_artifact_returns_none(self, tmp_path, sample_file):
        store = ArtifactStore(base_dir=str(tmp_path / "store"), ttl_minutes=0)
        info = store.store(sample_file)
        # Set created_at to the past
        meta_path = store.base_dir / f"{info.artifact_id}.meta"
        meta = json.loads(meta_path.read_text())
        past = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=2)).isoformat()
        meta["created_at"] = past
        meta_path.write_text(json.dumps(meta))
        result = store.get(info.artifact_id)
        assert result is None

    def test_get_missing_artifact_file_returns_none(self, tmp_store, sample_file):
        info = tmp_store.store(sample_file)
        # Delete the artifact file but keep meta
        artifact_path = tmp_store.base_dir / f"{info.artifact_id}.png"
        artifact_path.unlink()
        result = tmp_store.get(info.artifact_id)
        assert result is None


class TestCleanupExpired:

    def test_cleanup_removes_expired(self, tmp_path, sample_file):
        store = ArtifactStore(base_dir=str(tmp_path / "store"), ttl_minutes=0)
        info = store.store(sample_file)
        # Backdate the created_at
        meta_path = store.base_dir / f"{info.artifact_id}.meta"
        meta = json.loads(meta_path.read_text())
        past = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=2)).isoformat()
        meta["created_at"] = past
        meta_path.write_text(json.dumps(meta))
        removed = store.cleanup_expired()
        assert removed == 1

    def test_cleanup_keeps_fresh(self, tmp_store, sample_file):
        tmp_store.store(sample_file)
        removed = tmp_store.cleanup_expired()
        assert removed == 0

    def test_cleanup_handles_corrupt_meta(self, tmp_store):
        # Write a corrupt meta file
        corrupt_meta = tmp_store.base_dir / "corrupt-id.meta"
        corrupt_meta.write_text("not json")
        removed = tmp_store.cleanup_expired()
        assert removed == 1
        assert not corrupt_meta.exists()


class TestContentTypes:

    @pytest.mark.parametrize(
        "ext, expected",
        [
            (".png", "image/png"),
            (".jpg", "image/jpeg"),
            (".jpeg", "image/jpeg"),
            (".html", "text/html"),
            (".csv", "text/csv"),
            (".json", "application/json"),
            (".txt", "text/plain"),
        ],
    )
    def test_known_content_types(self, ext, expected):
        assert _CONTENT_TYPES[ext] == expected
