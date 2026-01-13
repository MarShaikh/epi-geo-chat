from typing import List
from src.rag.vector_store import CollectionVectorStore


def resolve_collections_by_keywords(
    data_type_keywords: List[str], limit: int = 3
) -> List[str]:
    """Resolves data type keywords to STAC collection IDs using semantic search.
    This function is called in the main workflow to map user data type requests to relevant collections.

    Args:
        data_type_keywords (List[str]): Keywords describing the type of collections to find.
        limit (int): Maximum number of collection IDs to return.

    Returns:
        List[str]: List of relevant STAC collection IDs.

    Example:
        >>> resolve_collections(["temperature", "thermal", "LST"])
        ['modis-11A1-061-nigeria-557', 'modis-11A2-061-nigeria']
    """
    vector_store = CollectionVectorStore()
    return vector_store.query_collections(data_type_keywords, n_results=limit)
