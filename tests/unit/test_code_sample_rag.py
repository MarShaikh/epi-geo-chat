"""
Tests for the CodeSampleStore RAG pipeline.

Uses a temporary in-memory ChromaDB client to avoid requiring a live server.
"""

import os
import uuid
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
SAMPLES_DIR = os.path.join(REPO_ROOT, "code_samples")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def in_memory_store():
    """Return a CodeSampleStore backed by an ephemeral in-process ChromaDB."""
    import chromadb
    from src.rag.code_sample_store import CodeSampleStore, SAMPLES_COLLECTION

    client = chromadb.EphemeralClient()
    # Use a unique collection name per test to guarantee isolation
    unique_name = f"{SAMPLES_COLLECTION}_{uuid.uuid4().hex}"
    collection = client.get_or_create_collection(name=unique_name)

    store = CodeSampleStore.__new__(CodeSampleStore)
    store.chroma_client = client
    store.collection = collection
    return store


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_index_samples_from_directory(in_memory_store):
    """Indexing the samples directory should add all .py files to the collection."""
    import glob

    expected = len(glob.glob(os.path.join(SAMPLES_DIR, "**", "*.py"), recursive=True))
    assert expected > 0, "No sample files found — check code_samples/ directory"

    n_indexed = in_memory_store.index_samples_from_directory(SAMPLES_DIR)
    assert n_indexed == expected, f"Expected {expected} files indexed, got {n_indexed}"
    assert in_memory_store.collection.count() == expected


def test_idempotent_indexing(in_memory_store):
    """Calling index_samples_from_directory twice should not duplicate entries."""
    in_memory_store.index_samples_from_directory(SAMPLES_DIR)
    count_after_first = in_memory_store.collection.count()

    n_indexed_second = in_memory_store.index_samples_from_directory(SAMPLES_DIR)
    assert n_indexed_second == 0, "Second indexing should skip already-indexed files"
    assert in_memory_store.collection.count() == count_after_first


def test_query_returns_results(in_memory_store):
    """After indexing, a semantic query should return results."""
    in_memory_store.index_samples_from_directory(SAMPLES_DIR)
    results = in_memory_store.query_samples("rainfall time series chart", n_results=2)
    assert len(results) == 2
    for r in results:
        assert "filepath" in r
        assert "source" in r
        assert "task_type" in r


def test_query_time_series_relevance(in_memory_store):
    """A time-series query should return a time_series sample as the top result."""
    in_memory_store.index_samples_from_directory(SAMPLES_DIR)
    results = in_memory_store.query_samples("plot monthly rainfall over time as a line chart", n_results=3)
    assert results, "Expected at least one result"
    top_task = results[0]["task_type"]
    assert top_task == "time_series", (
        f"Expected top result to be 'time_series', got '{top_task}'"
    )


def test_query_spatial_map_relevance(in_memory_store):
    """A spatial map query should return a spatial_maps sample as the top result."""
    in_memory_store.index_samples_from_directory(SAMPLES_DIR)
    results = in_memory_store.query_samples("show temperature distribution on a map with colorbar", n_results=3)
    assert results, "Expected at least one result"
    task_types = [r["task_type"] for r in results]
    assert "spatial_maps" in task_types, (
        f"Expected 'spatial_maps' in top results, got: {task_types}"
    )


def test_query_empty_store_returns_empty(in_memory_store):
    """Querying an empty store should return an empty list, not raise."""
    results = in_memory_store.query_samples("anything", n_results=3)
    assert results == []


def test_retrieve_code_samples_graceful_on_error():
    """retrieve_code_samples() should return [] and not raise if ChromaDB is unavailable."""
    from src.rag.code_sample_retriever import retrieve_code_samples

    with patch("src.rag.code_sample_retriever.CodeSampleStore") as MockStore:
        MockStore.side_effect = ConnectionError("ChromaDB unavailable")
        result = retrieve_code_samples("rainfall time series", n_results=3)
    assert result == []
