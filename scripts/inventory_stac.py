from src.stac.catalog_client import GeoCatalogClient
from dotenv import load_dotenv
import json
from pathlib import Path

load_dotenv()

client = GeoCatalogClient()
collections = client.list_collections()

inventory = {}
for coll in collections.get("collections", []):
    collection_id = coll["id"]

    try:
        collection = client.get_collection(collection_id)
        inventory[collection_id] = {
            "id": collection_id,
            "title": collection.get("title", ""),
            "description": collection.get("description", ""),
            "extent": collection.get("extent", {}),
            "license": collection.get("license", ""),
            "providers": collection.get("providers", []),
            "keywords": collection.get("keywords", []),
            "item_assets": list(collection.get("item_assets", {}).keys()),
        }
    except Exception as e:
        print(f"Error: {e}")
        inventory[collection_id] = {"error": str(e)}

# save to file
output_path = Path("data/stac_inventory.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, "w") as f:
    json.dump(inventory, f, indent=2)

print(f"Inventory saved to {output_path}")
