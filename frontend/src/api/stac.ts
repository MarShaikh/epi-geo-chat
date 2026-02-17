/** API client for STAC explorer endpoints. */

import type { STACCollection, STACFeatureCollection, STACFeature, STACSearchRequest } from "../types/api";

const API_BASE = "/api/v1";

export async function fetchCollections(): Promise<STACCollection[]> {
  const res = await fetch(`${API_BASE}/stac/collections`);
  if (!res.ok) throw new Error(`Failed to fetch collections: ${res.statusText}`);
  const data = await res.json();
  return data.collections ?? [];
}

export async function fetchCollection(id: string): Promise<STACCollection> {
  const res = await fetch(`${API_BASE}/stac/collections/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch collection: ${res.statusText}`);
  return res.json();
}

export async function searchItems(params: STACSearchRequest): Promise<STACFeatureCollection> {
  const res = await fetch(`${API_BASE}/stac/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error(`Search failed: ${res.statusText}`);
  return res.json();
}

export async function fetchItem(collectionId: string, itemId: string): Promise<STACFeature> {
  const res = await fetch(`${API_BASE}/stac/collections/${collectionId}/items/${itemId}`);
  if (!res.ok) throw new Error(`Failed to fetch item: ${res.statusText}`);
  return res.json();
}

export function buildTileUrl(
  collectionId: string,
  itemId: string,
  assets: string,
  opts?: { colormap?: string; rescale?: string; assetBidx?: string },
): string {
  const base = `${API_BASE}/tiles/${collectionId}/${itemId}/{z}/{x}/{y}.png?assets=${encodeURIComponent(assets)}`;
  const params: string[] = [];
  if (opts?.colormap) params.push(`colormap_name=${encodeURIComponent(opts.colormap)}`);
  if (opts?.rescale) params.push(`rescale=${encodeURIComponent(opts.rescale)}`);
  if (opts?.assetBidx) params.push(`asset_bidx=${encodeURIComponent(opts.assetBidx)}`);
  return params.length > 0 ? `${base}&${params.join("&")}` : base;
}
