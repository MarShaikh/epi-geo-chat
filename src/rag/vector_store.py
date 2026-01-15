import os
from typing import List
from dotenv import load_dotenv

import chromadb

load_dotenv()


class CollectionVectorStore:
    """
    Vector store for STAC collection items using ChromaDB.
    Used for semantic collection selection based on user keywords.
    """

    def __init__(self):

        self.chroma_client = chromadb.HttpClient(
            host=os.environ["CHROMA_CLIENT_URL"], ssl=True
        )

        try:
            self.chroma_client.heartbeat()
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to ChromaDB at {os.environ['CHROMA_CLIENT_URL']}: {e}"
            )

        self.collection = self.chroma_client.get_or_create_collection(
            name="stac_collections",
            metadata={"description": "STAC collection metadata for semantic search."},
        )

    def index_collections_from_api(self):
        """
        Index STAC collections directly from the GeoCatalog API.

        Creates rich text embeddings from:
        - Collection title and description
        - Keywords (critical for matching user queries)
        - Sensor/platform information
        - Temporal and spatial coverage
        """
        from src.stac.catalog_client import GeoCatalogClient

        catalog = GeoCatalogClient()
        collection_response = catalog.list_collections()

        documents = []
        metadatas = []
        ids = []

        for coll in collection_response.get("collections", []):
            coll_id = coll["id"]

            doc_text = f"""
            Title: {coll.get('title', '')}
            Description: {coll.get('description', '')}
            Keywords: {', '.join(coll.get('keywords', []))}
            License: {coll.get('license', '')}
            """

            # Extract useful metadata for retrieval
            spatial_extent = (
                coll.get("extent", {}).get("spatial", [[]]).get("bbox", [[]])[0]
            )
            temporal_extent = (
                coll.get("extent", {}).get("temporal", [[]]).get("interval", [[]])[0]
            )

            documents.append(doc_text.strip())
            metadatas.append(
                {
                    "collection_id": coll_id,
                    "title": coll.get("title", ""),
                    "keywords": f"{coll.get("keywords", [])}",
                    "spatial_extent": f"{spatial_extent}",
                    "temporal_extent": f"{temporal_extent}",
                }
            )
            ids.append(coll_id)
            print(metadatas)

        # Add to ChromaDB collection
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

        print(f"Indexed {len(ids)} STAC collections into ChromaDB vector store.")

    def query_collections(self, keywords: List[str], n_results: int = 3) -> List[str]:
        """
        Query the vector store for relevant STAC collections based on user keywords.

        Args:
            keywords (List[str]): List of user keywords to search for.
            n_results (int): Number of top results to return.
        Returns:
            List[str]: List of collection IDs for the top matching collections.
        """
        query_text = " ".join(keywords)

        results = self.collection.query(query_texts=[query_text], n_results=n_results)

        # Extract collection IDs from metadata
        if results.get("metadatas") and results["metadatas"]:
            collection_ids = [
                str(meta["collection_id"]) for meta in results["metadatas"][0]
            ]
        else:
            collection_ids = []

        return collection_ids
