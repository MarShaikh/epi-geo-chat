import os
import requests
from typing import List, Optional, Dict, Union

import pystac
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()


class GeoCatalogClient:
    def __init__(self):
        self.catalog_url = os.environ.get("GEOCATALOG_URL")
        self.scope = os.environ.get("GEOCATALOG_SCOPE")
        self.credential = DefaultAzureCredential()

    def _get_headers(self) -> Dict:
        if not self.scope:
            raise ValueError("GEOCATALOG_SCOPE environment variable is not set")
        token = self.credential.get_token(self.scope)
        return {"Authorization": f"Bearer {token.token}"}

    def list_collections(self) -> Dict:
        """List all collections in the catalog."""
        url = f"{self.catalog_url}/stac/collections"
        params = {"api-version": "2025-04-03-preview"}
        response = requests.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        return response.json()

    def get_collection(self, collection_id: str) -> Dict:
        """Get details of a specific collection."""
        url = f"{self.catalog_url}/stac/collections/{collection_id}"
        params = {"api-version": "2025-04-03-preview"}
        response = requests.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        return response.json()

    def search(
        self,
        bbox: Optional[List[float]] = None,
        datetime: Optional[str] = None,
        collections: Optional[List[str]] = None,
        limit: int = 10,
    ) -> Dict:
        """Search for items in the catalog based on spatial and temporal parameters."""
        url = f"{self.catalog_url}/stac/search"
        params = {"api-version": "2025-04-03-preview", "sign": "true"}

        body: Dict[str, Union[int, str, List[float], List[str]]] = {"limit": limit}
        if bbox:
            body["bbox"] = bbox
        if datetime:
            body["datetime"] = datetime
        if collections:
            body["collections"] = collections

        response = requests.post(
            url, headers=self._get_headers(), params=params, json=body
        )
        response.raise_for_status()
        return response.json()

    def get_item(self, collection_id: str, item_id: str) -> pystac.Item:
        """Get details of a specific item in a collection."""
        url = f"{self.catalog_url}/stac/collections/{collection_id}/items/{item_id}"
        params = {"api-version": "2025-04-03-preview", "sign": "true"}
        response = requests.get(url, headers=self._get_headers(), params=params)
        response.raise_for_status()
        return pystac.Item.from_dict(response.json(), migrate=True)
