from src.rag.vector_store import CollectionVectorStore
from dotenv import load_dotenv

load_dotenv()


def main():
    print("Indexing STAC collections into vector store from GeoCatalog API...")

    vector_store = CollectionVectorStore()
    vector_store.index_collections_from_api()

    test_cases = [
        (["rainfall", "precipitation"], "Rainfall query"),
        (["temperature", "LST", "thermal"], "Temperature query"),
        (["vegetation", "NDVI"], "Vegetation query"),
    ]
    print("\n" + "=" * 60)
    print("Testing semantic collection search:")
    print("=" * 60)

    for keywords, description in test_cases:
        collections = vector_store.query_collections(keywords, n_results=3)
        print(f"\n{description}")
        print(f"  Keywords: {keywords}")
        print(f"  Matched collections: {collections}")


if __name__ == "__main__":
    main()
