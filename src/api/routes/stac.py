"""STAC explorer endpoints — proxies GeoCatalog STAC API with Azure AD auth."""

import asyncio
import traceback
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.stac.catalog_client import GeoCatalogClient

router = APIRouter(prefix="/stac")

_client = GeoCatalogClient()


class SearchRequest(BaseModel):
    bbox: Optional[List[float]] = Field(default=None, min_length=4, max_length=4)
    datetime: Optional[str] = None
    collections: Optional[List[str]] = None
    limit: int = Field(default=20, ge=1, le=100)


@router.get("/collections")
async def list_collections():
    try:
        return await asyncio.to_thread(_client.list_collections)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/collections/{collection_id}")
async def get_collection(collection_id: str):
    try:
        return await asyncio.to_thread(_client.get_collection, collection_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/search")
async def search(request: SearchRequest):
    try:
        return await asyncio.to_thread(
            _client.search,
            bbox=request.bbox,
            datetime=request.datetime,
            collections=request.collections,
            limit=request.limit,
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/collections/{collection_id}/items/{item_id}")
async def get_item(collection_id: str, item_id: str):
    try:
        item = await asyncio.to_thread(_client.get_item, collection_id, item_id)
        return item.to_dict()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
