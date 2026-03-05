"""
Convenience wrapper for retrieving relevant code samples at generation time.
"""

from typing import List

from src.rag.code_sample_store import CodeSampleStore


def retrieve_code_samples(query: str, n_results: int = 3) -> List[dict]:
    """
    Return the top-N most relevant code samples for a given analysis query.

    Silently returns an empty list if the ChromaDB store is unavailable,
    so that code generation degrades gracefully without breaking the pipeline.

    Args:
        query: Natural language description of the analysis task.
        n_results: Number of examples to retrieve.

    Returns:
        List of dicts with keys: filepath, task_type, docstring, source.

    Example:
        >>> retrieve_code_samples("rainfall time series chart for Lagos")
        [{"filepath": "time_series/rainfall_time_series.py", "source": "...", ...}]
    """
    try:
        store = CodeSampleStore()
        return store.query_samples(query, n_results=n_results)
    except Exception as e:
        print(f"[CodeSampleRetriever] Could not retrieve samples: {e}")
        return []
