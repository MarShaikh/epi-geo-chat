"""Tile proxy — forwards requests to GeoCatalog Tiler API with Azure AD auth."""

import os
from typing import Optional

import requests as http_requests
from azure.identity import DefaultAzureCredential
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

router = APIRouter(prefix="/tiles")

_credential = DefaultAzureCredential()
_catalog_url = os.environ.get("GEOCATALOG_URL", "")
_scope = os.environ.get("GEOCATALOG_SCOPE", "")


def _get_token() -> str:
    return _credential.get_token(_scope).token


@router.get("/{collection_id}/{item_id}/{z}/{x}/{y}.png")
async def get_tile(
    collection_id: str,
    item_id: str,
    z: int,
    x: int,
    y: int,
    assets: str = Query(...),
    colormap_name: Optional[str] = Query(default=None),
    rescale: Optional[str] = Query(default=None),
    asset_bidx: Optional[str] = Query(default=None),
):
    url = (
        f"{_catalog_url}/data/collections/{collection_id}"
        f"/items/{item_id}/tiles/{z}/{x}/{y}@1x.png"
    )
    params = {
        "api-version": "2025-04-30-preview",
        "tileMatrixSetId": "WebMercatorQuad",
        "assets": assets,
    }
    if colormap_name:
        params["colormap_name"] = colormap_name
    if rescale:
        params["rescale"] = rescale
    if asset_bidx:
        params["asset_bidx"] = asset_bidx

    try:
        resp = http_requests.get(
            url,
            params=params,
            headers={"Authorization": f"Bearer {_get_token()}"},
            timeout=30,
        )
        resp.raise_for_status()
    except http_requests.exceptions.HTTPError:
        raise HTTPException(status_code=resp.status_code, detail="Tile fetch failed")
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return Response(
        content=resp.content,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/{collection_id}/{item_id}/bbox/{minx},{miny},{maxx},{maxy}.png")
async def get_bbox_image(
    collection_id: str,
    item_id: str,
    minx: float,
    miny: float,
    maxx: float,
    maxy: float,
    assets: str = Query(...),
    width: int = Query(default=1024),
    height: int = Query(default=1024),
    colormap_name: Optional[str] = Query(default=None),
    rescale: Optional[str] = Query(default=None),
    asset_bidx: Optional[str] = Query(default=None),
    nodata: Optional[str] = Query(default=None),
):
    url = (
        f"{_catalog_url}/data/collections/{collection_id}"
        f"/items/{item_id}/crop/{minx},{miny},{maxx},{maxy}/{width}x{height}.png"
    )
    params: dict[str, str] = {
        "api-version": "2025-04-30-preview",
        "assets": assets,
    }
    if colormap_name:
        params["colormap_name"] = colormap_name
    if rescale:
        params["rescale"] = rescale
    if asset_bidx:
        params["asset_bidx"] = asset_bidx
    if nodata:
        params["nodata"] = nodata

    try:
        resp = http_requests.get(
            url,
            params=params,
            headers={"Authorization": f"Bearer {_get_token()}"},
            timeout=60,
        )
        resp.raise_for_status()
    except http_requests.exceptions.HTTPError:
        print(f"Bbox image failed ({resp.status_code}): {resp.text[:500]}")
        raise HTTPException(status_code=resp.status_code, detail=resp.text[:200])
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return Response(
        content=resp.content,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=3600"},
    )
